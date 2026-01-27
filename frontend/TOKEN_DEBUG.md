/**
 * Token Debugging Guide
 * 
 * If you're getting 401 Unauthorized on /api/evaluations/history/:
 * 
 * 1. Check if localStorage has tokens:
 *    - localStorage.getItem('access_token')
 *    - localStorage.getItem('refresh_token')
 * 
 * 2. If tokens exist, decode them to check expiration:
 *    - Use jwt.decode() or check the payload at jwt.io
 * 
 * 3. Check browser console for network errors
 * 
 * 4. Ensure you're logged in first:
 *    - POST /api/auth/login/ with credentials
 *    - Should return: { success: true, access: "...", refresh: "...", user: {...} }
 * 
 * 5. Then try to access history:
 *    - GET /api/evaluations/history/
 *    - With header: Authorization: Bearer <access_token>
 */

// Test endpoint (run in browser console):
async function testToken() {
  const token = localStorage.getItem('access_token');
  const response = await fetch('https://tanlov.kuprikqurilish.uz/api/evaluations/history/', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    }
  });
  
  console.log('Status:', response.status);
  console.log('Response:', await response.json());
}

// testToken();
