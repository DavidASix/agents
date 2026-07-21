# Extraction Patterns

How to extract testable decision logic from I/O-coupled functions.

## Pattern: Decision function extraction

### Before (untestable)

`getUserAccessLevel` in `src/server/access.ts` determines a user's access level. The decision logic (which level to assign based on entitlement status, partner programs, and onboarding windows) is interleaved with a complex database query:

```typescript
// src/server/access.ts
async function getUserAccessLevel(userId: number): Promise<AccessLevel> {
  try {
    // DB call: complex join across users, entitlements, contracts,
    // pricing catalog, and partner-program rules
    const [user] = await db
      .select({
        userId: users.id,
        email: users.email,
        onboardingStartDate: users.onboardingStartDate,
        entitlementActive: entitlements.active,
        contractStatus: contracts.status,
        planCode: products.planCode,
        programEligible: partnerPrograms.enabled,
        programWindowEndDate: partnerPrograms.windowEndDate,
      })
      .from(users)
      .leftJoin(entitlements, eq(entitlements.userId, users.id))
      .leftJoin(contracts, eq(entitlements.contractId, contracts.id))
      .leftJoin(prices, eq(contracts.priceId, prices.id))
      .leftJoin(products, eq(prices.productId, products.id))
      .leftJoin(partnerPrograms /* partner eligibility matching logic */)
      .where(eq(users.id, userId))
      .orderBy(desc(entitlements.active), desc(partnerPrograms.enabled))
      .limit(1);

    if (!user) return 'none';

    // Decision (buried): active entitlement with recognized plan
    if (
      user.entitlementActive &&
      ACTIVE_CONTRACT_STATUSES.includes(user.contractStatus ?? '') &&
      user.planCode
    ) {
      const level = PLAN_CODE_TO_ACCESS_LEVEL[user.planCode];
      if (level) return level;
      return 'standard'; // fallback for unrecognized plans
    }

    // Decision (buried): partner program window
    if (user.programEligible) {
      if (
        user.programWindowEndDate &&
        calculateDaysLeftInProgramWindow(new Date(user.programWindowEndDate)) > 0 &&
        !isProgramWindowEndDatePast(new Date(user.programWindowEndDate))
      ) {
        return 'program-window';
      }
    }

    // Decision (buried): onboarding access window
    if (user.onboardingStartDate) {
      if (calculateDaysLeftInOnboardingWindow(new Date(user.onboardingStartDate)) > 0)
        return 'onboarding-window';
    }

    return 'none';
  } catch (error) {
    return 'none';
  }
}
```

Testing this requires mocking a 5-table join. The test ends up reconstructing database state rather than verifying the access decisions.

### After (testable)

Extract the decision logic into a pure function. This is what `computeAccessState` in `src/domain/access-state.ts` does:

```typescript
// src/domain/access-state.ts — Pure decision function (no I/O)

export interface ComputeAccessStateParams {
  hasPaidEntitlement: boolean;
  onboardingStartDate: Date | null;
  hasProgramEligibility: boolean;
  programWindowEndDate: Date | null;
}

export function computeAccessState({
  hasPaidEntitlement,
  onboardingStartDate,
  hasProgramEligibility,
  programWindowEndDate,
}: ComputeAccessStateParams): AccessState {
  if (hasPaidEntitlement) {
    return { status: 'active', source: 'entitlement', daysRemaining: null /* ... */ };
  }

  const onboardingDaysRemaining = onboardingStartDate
    ? calculateDaysLeftInOnboardingWindow(onboardingStartDate)
    : null;
  const programDaysRemaining =
    hasProgramEligibility && programWindowEndDate
      ? calculateDaysLeftInProgramWindow(programWindowEndDate)
      : null;

  const isOnboardingActive = (onboardingDaysRemaining ?? 0) > 0;
  const isProgramActive = (programDaysRemaining ?? 0) > 0;

  // Prefer the larger active window when both are available.
  if (hasProgramEligibility) {
    if (
      isOnboardingActive &&
      (!isProgramActive || onboardingDaysRemaining! > programDaysRemaining!)
    ) {
      return {
        status: 'onboarding-window',
        source: 'onboarding',
        daysRemaining: onboardingDaysRemaining! /* ... */,
      };
    }
    if (isProgramActive) {
      return {
        status: 'program-window',
        source: 'program',
        daysRemaining: programDaysRemaining! /* ... */,
      };
    }
    return {
      status: 'program-eligible-expired',
      source: programWindowEndDate ? 'program' : 'none' /* ... */,
    };
  }

  if (isOnboardingActive) {
    return {
      status: 'onboarding-window',
      source: 'onboarding',
      daysRemaining: onboardingDaysRemaining! /* ... */,
    };
  }

  return { status: 'inactive', source: 'none', daysRemaining: 0 /* ... */ };
}
```

The orchestrator fetches data, then calls the decision function:

```typescript
// src/server/authorization.ts — Orchestrator (I/O + decision)
export async function getIsAccessRestrictedFromServer(
  id: number,
  email: string | null,
  onboardingStartDate: Date | null,
) {
  const entitlementsResult = await getEntitlementsByUserId(id);
  const entitlements = entitlementsResult.isOk() ? entitlementsResult.value : [];
  const hasPaidEntitlement = entitlements?.find((row) => row.active) ? true : false;
  const programEligibility = await getProgramEligibilityByEmail(email!);

  return isAccessRestricted({
    hasPaidEntitlement,
    onboardingStartDate,
    hasProgramEligibility: Boolean(programEligibility),
    programWindowEndDate: programEligibility?.windowEndDate ?? null,
  });
}
```

Now the decision logic is independently testable without any database:

```typescript
// src/domain/__tests__/access-state.test.ts
describe('computeAccessState', () => {
  it('returns active when user has paid entitlement', () => {
    vi.setSystemTime(new Date('2026-02-04T12:00:00.000Z'));
    const result = computeAccessState({
      hasPaidEntitlement: true,
      onboardingStartDate: new Date('2026-01-01T00:00:00.000Z'),
      hasProgramEligibility: true,
      programWindowEndDate: new Date('2026-06-01T12:00:00.000Z'),
    });
    expect(result.status).toBe('active');
    expect(result.daysRemaining).toBe(null);
  });

  it('prefers onboarding window when it has more days remaining', () => {
    vi.setSystemTime(new Date('2025-06-25T12:00:00.000Z'));
    const result = computeAccessState({
      hasPaidEntitlement: false,
      onboardingStartDate: new Date('2025-06-20T00:00:00.000Z'),
      hasProgramEligibility: true,
      programWindowEndDate: new Date('2025-06-26T12:00:00.000Z'),
    });
    expect(result.status).toBe('onboarding-window');
    expect(result.source).toBe('onboarding');
  });

  it('prefers program window when onboarding and program days are equal', () => {
    vi.setSystemTime(new Date('2025-07-01T00:00:00.000Z'));
    const result = computeAccessState({
      hasPaidEntitlement: false,
      onboardingStartDate: new Date('2025-06-25T00:00:00.000Z'),
      hasProgramEligibility: true,
      programWindowEndDate: new Date('2025-07-09T12:00:00.000Z'),
    });
    expect(result.status).toBe('program-window');
    expect(result.source).toBe('program');
  });

  it('returns onboarding-window when program window is expired but onboarding is active', () => {
    vi.setSystemTime(new Date('2025-07-10T00:00:00.000Z'));
    const result = computeAccessState({
      hasPaidEntitlement: false,
      onboardingStartDate: new Date('2025-07-05T00:00:00.000Z'),
      hasProgramEligibility: true,
      programWindowEndDate: new Date('2025-07-01T12:00:00.000Z'),
    });
    expect(result.status).toBe('onboarding-window');
    expect(result.source).toBe('onboarding');
    expect(result.onboardingDaysRemaining).toBeGreaterThan(0);
    expect(result.programDaysRemaining).toBe(0);
  });

  it('returns inactive for user without eligibility and no onboarding start date', () => {
    vi.setSystemTime(new Date('2025-06-25T12:00:00.000Z'));
    const result = computeAccessState({
      hasPaidEntitlement: false,
      onboardingStartDate: null,
      hasProgramEligibility: false,
      programWindowEndDate: null,
    });
    expect(result.status).toBe('inactive');
    expect(result.source).toBe('none');
  });
});
```

## When to extract vs. when to mock

Extract when:

- The function has 3+ decision branches interleaved with I/O
- The decisions encode security invariants or business rules
- The same decision logic is reused across multiple callers
- Testing via mocks would require reconstructing complex state

Mock (or use integration tests) when:

- The logic IS the I/O (e.g., "does this query return the right rows?")
- The function is simple orchestration with no significant branching
- You're testing that components are wired together correctly

## Return type design for decision functions

Use discriminated unions that force callers to handle all cases:

```typescript
// Status union with source tracking — from src/domain/access-state.ts
type AccessStateStatus =
  | 'active' // paid entitlement
  | 'program-window' // partner or campaign access window
  | 'onboarding-window' // introductory access window
  | 'program-eligible-expired' // eligible, but no active program window
  | 'inactive'; // no access

interface AccessState {
  status: AccessStateStatus;
  source: 'entitlement' | 'program' | 'onboarding' | 'none';
  daysRemaining: number | null;
  onboardingDaysRemaining: number | null;
  programDaysRemaining: number | null;
  hasProgramEligibility: boolean;
}
```

Benefits:

- The status + source fields make tests self-documenting
- The discriminated union prevents "forgot to handle this case" bugs
- Downstream consumers like `isAccessRestrictedFromState` can make simple decisions on the result

## Granularity

Each extracted function should represent one coherent decision:

- `computeAccessState` — determines access status from user attributes
- `isAccessRestrictedFromState` — derives a boolean access check from state
- `isAccessRestricted` — convenience wrapper combining both

The orchestrator (`getIsAccessRestrictedFromServer`) handles I/O: fetching entitlements, looking up program eligibility, then passing plain data to the decision functions.

Avoid extracting a single `checkAllAccess(allTheData)` function. That just moves the untestable monolith. The value is in small, focused functions where each test clearly states what invariant it protects.

## Other neutral domains this pattern fits

- Launch cohorts + regional rollout windows
- Education grants + student onboarding windows
- Enterprise contract access + temporary migration windows
