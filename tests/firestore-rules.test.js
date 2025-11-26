/**
 * Firestore Security Rules Tests
 * 
 * Tests the security rules defined in firestore.rules
 * Run with: firebase emulators:exec --only firestore 'npm test'
 */

const { initializeTestEnvironment, assertSucceeds, assertFails } = require('@firebase/rules-unit-testing');
const { setLogLevel } = require('firebase/firestore');

// Disable logging for cleaner test output
setLogLevel('error');

let testEnv;

// Test data
const PARENT_USER_ID = 'parent-user-1';
const CHILD_USER_ID = 'child-user-1';
const OTHER_USER_ID = 'other-user-1';
const FAMILY_ID = 'family-1';
const OTHER_FAMILY_ID = 'family-2';
const ACTIVITY_ID = 'activity-1';
const LOG_ID = 'log-1';

beforeAll(async () => {
  testEnv = await initializeTestEnvironment({
    projectId: 'test-project',
    firestore: {
      rules: require('fs').readFileSync('../firestore.rules', 'utf8'),
      host: 'localhost',
      port: 8080
    }
  });
});

afterAll(async () => {
  await testEnv.cleanup();
});

beforeEach(async () => {
  await testEnv.clearFirestore();
});

describe('Users Collection Security Rules', () => {
  test('User can read their own profile', async () => {
    const db = testEnv.authenticatedContext(PARENT_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(PARENT_USER_ID).set({
        email: 'parent@example.com',
        role: 'parent',
        familyId: FAMILY_ID
      });
    });

    await assertSucceeds(db.collection('users').doc(PARENT_USER_ID).get());
  });

  test('User cannot read another user profile from different family', async () => {
    const db = testEnv.authenticatedContext(PARENT_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(PARENT_USER_ID).set({
        email: 'parent@example.com',
        role: 'parent',
        familyId: FAMILY_ID
      });
      await context.firestore().collection('users').doc(OTHER_USER_ID).set({
        email: 'other@example.com',
        role: 'parent',
        familyId: OTHER_FAMILY_ID
      });
    });

    await assertFails(db.collection('users').doc(OTHER_USER_ID).get());
  });

  test('User can read family member profile', async () => {
    const db = testEnv.authenticatedContext(PARENT_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(PARENT_USER_ID).set({
        email: 'parent@example.com',
        role: 'parent',
        familyId: FAMILY_ID
      });
      await context.firestore().collection('users').doc(CHILD_USER_ID).set({
        email: 'child@example.com',
        role: 'child',
        familyId: FAMILY_ID
      });
    });

    await assertSucceeds(db.collection('users').doc(CHILD_USER_ID).get());
  });

  test('User can create their own profile', async () => {
    const db = testEnv.authenticatedContext(PARENT_USER_ID).firestore();
    
    await assertSucceeds(db.collection('users').doc(PARENT_USER_ID).set({
      email: 'parent@example.com',
      role: 'parent',
      familyId: null
    }));
  });

  test('User cannot create profile for another user', async () => {
    const db = testEnv.authenticatedContext(PARENT_USER_ID).firestore();
    
    await assertFails(db.collection('users').doc(OTHER_USER_ID).set({
      email: 'other@example.com',
      role: 'parent',
      familyId: null
    }));
  });

  test('Unauthenticated user cannot read profiles', async () => {
    const db = testEnv.unauthenticatedContext().firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(PARENT_USER_ID).set({
        email: 'parent@example.com',
        role: 'parent',
        familyId: FAMILY_ID
      });
    });

    await assertFails(db.collection('users').doc(PARENT_USER_ID).get());
  });
});

describe('Families Collection Security Rules', () => {
  test('Parent can create a family', async () => {
    const db = testEnv.authenticatedContext(PARENT_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(PARENT_USER_ID).set({
        email: 'parent@example.com',
        role: 'parent',
        familyId: null
      });
    });

    await assertSucceeds(db.collection('families').doc(FAMILY_ID).set({
      inviteCode: 'ABC123',
      ownerId: PARENT_USER_ID,
      members: [PARENT_USER_ID],
      createdAt: new Date()
    }));
  });

  test('Child cannot create a family', async () => {
    const db = testEnv.authenticatedContext(CHILD_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(CHILD_USER_ID).set({
        email: 'child@example.com',
        role: 'child',
        familyId: null
      });
    });

    await assertFails(db.collection('families').doc(FAMILY_ID).set({
      inviteCode: 'ABC123',
      ownerId: CHILD_USER_ID,
      members: [CHILD_USER_ID],
      createdAt: new Date()
    }));
  });

  test('Family member can read their family', async () => {
    const db = testEnv.authenticatedContext(PARENT_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(PARENT_USER_ID).set({
        email: 'parent@example.com',
        role: 'parent',
        familyId: FAMILY_ID
      });
      await context.firestore().collection('families').doc(FAMILY_ID).set({
        inviteCode: 'ABC123',
        ownerId: PARENT_USER_ID,
        members: [PARENT_USER_ID]
      });
    });

    await assertSucceeds(db.collection('families').doc(FAMILY_ID).get());
  });

  test('User cannot read another family', async () => {
    const db = testEnv.authenticatedContext(PARENT_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(PARENT_USER_ID).set({
        email: 'parent@example.com',
        role: 'parent',
        familyId: FAMILY_ID
      });
      await context.firestore().collection('families').doc(OTHER_FAMILY_ID).set({
        inviteCode: 'XYZ789',
        ownerId: OTHER_USER_ID,
        members: [OTHER_USER_ID]
      });
    });

    await assertFails(db.collection('families').doc(OTHER_FAMILY_ID).get());
  });
});

describe('Activities Collection Security Rules', () => {
  test('Parent can create activity for their family', async () => {
    const db = testEnv.authenticatedContext(PARENT_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(PARENT_USER_ID).set({
        email: 'parent@example.com',
        role: 'parent',
        familyId: FAMILY_ID
      });
    });

    await assertSucceeds(db.collection('activities').doc(ACTIVITY_ID).set({
      familyId: FAMILY_ID,
      name: 'Reading',
      unit: 'Pomodoro',
      rate: 1.0,
      createdBy: PARENT_USER_ID,
      createdAt: new Date()
    }));
  });

  test('Child cannot create activity', async () => {
    const db = testEnv.authenticatedContext(CHILD_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(CHILD_USER_ID).set({
        email: 'child@example.com',
        role: 'child',
        familyId: FAMILY_ID
      });
    });

    await assertFails(db.collection('activities').doc(ACTIVITY_ID).set({
      familyId: FAMILY_ID,
      name: 'Reading',
      unit: 'Pomodoro',
      rate: 1.0,
      createdBy: CHILD_USER_ID,
      createdAt: new Date()
    }));
  });

  test('Family member can read family activities', async () => {
    const db = testEnv.authenticatedContext(CHILD_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(CHILD_USER_ID).set({
        email: 'child@example.com',
        role: 'child',
        familyId: FAMILY_ID
      });
      await context.firestore().collection('activities').doc(ACTIVITY_ID).set({
        familyId: FAMILY_ID,
        name: 'Reading',
        unit: 'Pomodoro',
        rate: 1.0,
        createdBy: PARENT_USER_ID,
        createdAt: new Date()
      });
    });

    await assertSucceeds(db.collection('activities').doc(ACTIVITY_ID).get());
  });

  test('Parent can delete activity from their family', async () => {
    const db = testEnv.authenticatedContext(PARENT_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(PARENT_USER_ID).set({
        email: 'parent@example.com',
        role: 'parent',
        familyId: FAMILY_ID
      });
      await context.firestore().collection('activities').doc(ACTIVITY_ID).set({
        familyId: FAMILY_ID,
        name: 'Reading',
        unit: 'Pomodoro',
        rate: 1.0,
        createdBy: PARENT_USER_ID,
        createdAt: new Date()
      });
    });

    await assertSucceeds(db.collection('activities').doc(ACTIVITY_ID).delete());
  });

  test('Child cannot delete activity', async () => {
    const db = testEnv.authenticatedContext(CHILD_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(CHILD_USER_ID).set({
        email: 'child@example.com',
        role: 'child',
        familyId: FAMILY_ID
      });
      await context.firestore().collection('activities').doc(ACTIVITY_ID).set({
        familyId: FAMILY_ID,
        name: 'Reading',
        unit: 'Pomodoro',
        rate: 1.0,
        createdBy: PARENT_USER_ID,
        createdAt: new Date()
      });
    });

    await assertFails(db.collection('activities').doc(ACTIVITY_ID).delete());
  });
});

describe('Logs Collection Security Rules', () => {
  test('Child can create log entry for their family', async () => {
    const db = testEnv.authenticatedContext(CHILD_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(CHILD_USER_ID).set({
        email: 'child@example.com',
        role: 'child',
        familyId: FAMILY_ID
      });
    });

    await assertSucceeds(db.collection('logs').doc(LOG_ID).set({
      activityId: ACTIVITY_ID,
      userId: CHILD_USER_ID,
      familyId: FAMILY_ID,
      units: 1,
      timestamp: new Date(),
      verificationStatus: 'pending',
      verifiedBy: null,
      verifiedAt: null
    }));
  });

  test('Family member can read family logs', async () => {
    const db = testEnv.authenticatedContext(PARENT_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(PARENT_USER_ID).set({
        email: 'parent@example.com',
        role: 'parent',
        familyId: FAMILY_ID
      });
      await context.firestore().collection('logs').doc(LOG_ID).set({
        activityId: ACTIVITY_ID,
        userId: CHILD_USER_ID,
        familyId: FAMILY_ID,
        units: 1,
        timestamp: new Date(),
        verificationStatus: 'pending',
        verifiedBy: null,
        verifiedAt: null
      });
    });

    await assertSucceeds(db.collection('logs').doc(LOG_ID).get());
  });

  test('Parent can update log verification status', async () => {
    const db = testEnv.authenticatedContext(PARENT_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(PARENT_USER_ID).set({
        email: 'parent@example.com',
        role: 'parent',
        familyId: FAMILY_ID
      });
      await context.firestore().collection('logs').doc(LOG_ID).set({
        activityId: ACTIVITY_ID,
        userId: CHILD_USER_ID,
        familyId: FAMILY_ID,
        units: 1,
        timestamp: new Date(),
        verificationStatus: 'pending',
        verifiedBy: null,
        verifiedAt: null
      });
    });

    await assertSucceeds(db.collection('logs').doc(LOG_ID).update({
      verificationStatus: 'approved',
      verifiedBy: PARENT_USER_ID,
      verifiedAt: new Date()
    }));
  });

  test('Child cannot update log verification status', async () => {
    const db = testEnv.authenticatedContext(CHILD_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(CHILD_USER_ID).set({
        email: 'child@example.com',
        role: 'child',
        familyId: FAMILY_ID
      });
      await context.firestore().collection('logs').doc(LOG_ID).set({
        activityId: ACTIVITY_ID,
        userId: CHILD_USER_ID,
        familyId: FAMILY_ID,
        units: 1,
        timestamp: new Date(),
        verificationStatus: 'pending',
        verifiedBy: null,
        verifiedAt: null
      });
    });

    await assertFails(db.collection('logs').doc(LOG_ID).update({
      verificationStatus: 'approved'
    }));
  });

  test('User cannot read logs from another family', async () => {
    const db = testEnv.authenticatedContext(PARENT_USER_ID).firestore();
    await testEnv.withSecurityRulesDisabled(async (context) => {
      await context.firestore().collection('users').doc(PARENT_USER_ID).set({
        email: 'parent@example.com',
        role: 'parent',
        familyId: FAMILY_ID
      });
      await context.firestore().collection('logs').doc(LOG_ID).set({
        activityId: ACTIVITY_ID,
        userId: OTHER_USER_ID,
        familyId: OTHER_FAMILY_ID,
        units: 1,
        timestamp: new Date(),
        verificationStatus: 'pending',
        verifiedBy: null,
        verifiedAt: null
      });
    });

    await assertFails(db.collection('logs').doc(LOG_ID).get());
  });
});
