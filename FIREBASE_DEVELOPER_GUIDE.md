# Firebase Developer Guide

Quick reference for working with Firebase in the Gamified Activity Tracker.

## Real-time Hooks

### useActivities
Fetches activities with real-time updates.

```typescript
import { useActivities } from '@/hooks/useActivities';

function MyComponent() {
  const { activities, isLoading, error } = useActivities(familyId);
  
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  
  return <div>{activities.map(a => ...)}</div>;
}
```

### useLogs
Fetches logs with optional filters.

```typescript
import { useLogs, usePendingLogsForVerification, useUserLogs } from '@/hooks/useLogs';

// All logs for a family
const { logs, isLoading, error } = useLogs(familyId);

// Pending logs only (for parent verification)
const { logs, isLoading, error } = usePendingLogsForVerification(familyId);

// User's logs
const { logs, isLoading, error } = useUserLogs(familyId, userId);
```

### useFamily
Fetches family data and members.

```typescript
import { useFamily, useFamilyMembers, useFamilyChildren } from '@/hooks/useFamily';

// Family data
const { family, isLoading, error } = useFamily(familyId);

// All family members
const { members, isLoading, error } = useFamilyMembers(familyId);

// Children only (for parent view)
const { children, isLoading, error } = useFamilyChildren(familyId);
```

## Error Handling

### Frontend

```typescript
import { 
  getFirebaseErrorMessage,
  retryOperation,
  validateDocumentData,
  safeGetField,
  connectionMonitor
} from '@/lib/firebaseErrorHandler';

// Get user-friendly error message
try {
  // Firebase operation
} catch (error) {
  const message = getFirebaseErrorMessage(error);
  console.error(message);
}

// Retry operation with exponential backoff
const result = await retryOperation(
  async () => {
    // Your Firebase operation
    return await someFirebaseCall();
  },
  { maxAttempts: 3, initialDelay: 1000 }
);

// Validate document data
const data = doc.data();
validateDocumentData(data, ['requiredField1', 'requiredField2']);

// Safe field access
const value = safeGetField(data, 'fieldName', defaultValue);

// Monitor connection status
const unsubscribe = connectionMonitor.subscribe((isOnline) => {
  console.log('Connection status:', isOnline);
});
```

### Backend

```python
from utils.firebase_error_handler import (
    get_firebase_error_message,
    retry_operation,
    with_retry,
    validate_document_data,
    safe_get_field,
    RetryConfig,
    FirebaseErrorHandler
)

# Get user-friendly error message
try:
    # Firebase operation
except Exception as error:
    message = get_firebase_error_message(error)
    logger.error(message)

# Retry with decorator
@with_retry(RetryConfig(max_attempts=3))
def my_firebase_operation():
    # Your Firebase operation
    return db.collection('users').document(user_id).get()

# Retry with function
result = retry_operation(
    lambda: db.collection('users').document(user_id).get(),
    RetryConfig(max_attempts=3)
)

# Validate document data
data = doc.to_dict()
validate_document_data(data, ['required_field1', 'required_field2'])

# Safe field access
value = safe_get_field(data, 'field_name', default_value)

# Context manager for error handling
with FirebaseErrorHandler("fetch user data"):
    user_doc = db.collection('users').document(user_id).get()
```

## Security Rules Testing

### Setup
```bash
# Install dependencies
npm install
cd tests && npm install
```

### Run Tests
```bash
# Start emulator and run tests
firebase emulators:exec --only firestore 'cd tests && npm test'

# Or manually
firebase emulators:start
# In another terminal:
cd tests && npm test
```

### Add New Test
```javascript
test('Description of what you are testing', async () => {
  const db = testEnv.authenticatedContext(USER_ID).firestore();
  
  // Setup test data with security rules disabled
  await testEnv.withSecurityRulesDisabled(async (context) => {
    await context.firestore().collection('users').doc(USER_ID).set({
      // test data
    });
  });

  // Test with security rules enabled
  await assertSucceeds(db.collection('users').doc(USER_ID).get());
  // or
  await assertFails(db.collection('users').doc(OTHER_USER_ID).get());
});
```

## Common Patterns

### Creating a Document
```typescript
// Frontend
import { collection, addDoc, serverTimestamp } from 'firebase/firestore';
import { db } from '@/lib/firebase';

const docRef = await addDoc(collection(db, 'activities'), {
  familyId: familyId,
  name: 'Reading',
  unit: 'Pomodoro',
  rate: 1.0,
  createdBy: userId,
  createdAt: serverTimestamp()
});
```

```python
# Backend
from firebase_admin import firestore

db = firestore.client()
doc_ref = db.collection('activities').document()
doc_ref.set({
    'familyId': family_id,
    'name': 'Reading',
    'unit': 'Pomodoro',
    'rate': 1.0,
    'createdBy': user_id,
    'createdAt': firestore.SERVER_TIMESTAMP
})
```

### Updating a Document
```typescript
// Frontend
import { doc, updateDoc } from 'firebase/firestore';

await updateDoc(doc(db, 'logs', logId), {
  verificationStatus: 'approved',
  verifiedBy: parentId,
  verifiedAt: serverTimestamp()
});
```

```python
# Backend
doc_ref = db.collection('logs').document(log_id)
doc_ref.update({
    'verificationStatus': 'approved',
    'verifiedBy': parent_id,
    'verifiedAt': firestore.SERVER_TIMESTAMP
})
```

### Querying with Filters
```typescript
// Frontend
import { collection, query, where, orderBy, onSnapshot } from 'firebase/firestore';

const q = query(
  collection(db, 'logs'),
  where('familyId', '==', familyId),
  where('verificationStatus', '==', 'pending'),
  orderBy('timestamp', 'desc')
);

const unsubscribe = onSnapshot(q, (snapshot) => {
  snapshot.forEach((doc) => {
    console.log(doc.id, doc.data());
  });
});
```

```python
# Backend
logs_ref = db.collection('logs')
query = logs_ref.where('familyId', '==', family_id) \
               .where('verificationStatus', '==', 'pending') \
               .order_by('timestamp', direction=firestore.Query.DESCENDING)

docs = query.stream()
for doc in docs:
    print(doc.id, doc.to_dict())
```

### Batch Operations
```typescript
// Frontend
import { writeBatch, doc } from 'firebase/firestore';

const batch = writeBatch(db);
batch.update(doc(db, 'logs', logId1), { status: 'approved' });
batch.update(doc(db, 'logs', logId2), { status: 'approved' });
await batch.commit();
```

```python
# Backend
batch = db.batch()
batch.update(db.collection('logs').document(log_id1), {'status': 'approved'})
batch.update(db.collection('logs').document(log_id2), {'status': 'approved'})
batch.commit()
```

## Debugging Tips

### Enable Firestore Debug Logging
```typescript
// Frontend
import { setLogLevel } from 'firebase/firestore';
setLogLevel('debug');
```

```python
# Backend
import logging
logging.getLogger('firebase_admin').setLevel(logging.DEBUG)
```

### Check Security Rules
```bash
# Test rules in emulator UI
firebase emulators:start
# Open http://localhost:4000
```

### Monitor Real-time Listeners
```typescript
const unsubscribe = onSnapshot(
  query,
  (snapshot) => {
    console.log('Snapshot received:', snapshot.size, 'documents');
    snapshot.docChanges().forEach((change) => {
      console.log('Change type:', change.type, 'Doc:', change.doc.id);
    });
  },
  (error) => {
    console.error('Listener error:', error);
  }
);
```

### Check Indexes
If you get an error about missing indexes, the error message will include a link to create the index automatically in the Firebase Console.

## Performance Tips

1. **Use indexes** - All composite queries need indexes
2. **Limit listener scope** - Only listen to data you need
3. **Unsubscribe listeners** - Always clean up in useEffect
4. **Batch operations** - Use batch writes for multiple updates
5. **Avoid N+1 queries** - Fetch related data in parallel
6. **Cache data** - Use React state to avoid redundant queries
7. **Pagination** - Implement for large datasets

## Security Best Practices

1. **Never trust client** - Always validate on backend
2. **Use security rules** - Second layer of defense
3. **Validate tokens** - Check auth on every request
4. **Check family membership** - Verify user belongs to family
5. **Sanitize inputs** - Prevent injection attacks
6. **Log security events** - Monitor for suspicious activity
7. **Rate limit** - Prevent abuse

## Common Errors

### "Missing or insufficient permissions"
- Check security rules
- Verify user is authenticated
- Confirm user belongs to the family

### "The query requires an index"
- Click the link in the error message
- Or add to firestore.indexes.json and deploy

### "Listener failed: unavailable"
- Network connection issue
- Will auto-retry with exponential backoff
- Check ConnectionStatus component

### "Document data is corrupted"
- Use validateDocumentData to check
- Use safeGetField for safe access
- Log error and skip document

## Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
- [Firebase Emulator Suite](https://firebase.google.com/docs/emulator-suite)
- [React Firebase Hooks](https://github.com/CSFrequency/react-firebase-hooks)
