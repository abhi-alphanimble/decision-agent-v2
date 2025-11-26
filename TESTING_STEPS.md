# Testing Steps for Member Join Feature

## Prerequisites
- Server is running (`python run.py`)
- Ngrok tunnel is active
- Slack app is configured with `member_joined_channel` event subscription
- Bot is added to a test channel

## Test Scenario 1: New Member Joins Channel with Pending Decisions

### Setup
1. Create a pending decision in a test channel:
   ```
   /decision propose "Should we use TypeScript for the frontend?"
   ```

2. Note the decision ID from the response

### Test Steps
1. Have a new user (who hasn't joined the channel yet) join the test channel
2. **Expected Result:**
   - New user receives a welcome message (only visible to them)
   - Message lists the pending decision
   - Message includes voting instructions
   - Server logs show: `👋 Member [username] ([user_id]) joined channel [channel_id]`
   - Server logs show: `✅ Sent welcome message to [username] with 1 pending decisions`

3. Verify the new member can vote:
   ```
   /decision approve [decision_id]
   ```
   
4. **Expected Result:**
   - Vote is recorded successfully
   - Decision approval count increases
   - No errors in server logs

## Test Scenario 2: New Member Joins Channel with NO Pending Decisions

### Setup
1. Ensure the test channel has no pending decisions
   - Use `/decision list pending` to verify
   - If there are pending decisions, approve or reject them

### Test Steps
1. Have a new user join the test channel
2. **Expected Result:**
   - New user receives a welcome message
   - Message says "There are currently no pending decisions"
   - Message includes general bot usage instructions
   - Server logs show member join event
   - No errors in server logs

## Test Scenario 3: Multiple Pending Decisions

### Setup
1. Create 3-5 pending decisions in the test channel:
   ```
   /decision propose "Decision 1"
   /decision propose "Decision 2"
   /decision propose "Decision 3"
   ```

### Test Steps
1. Have a new user join the test channel
2. **Expected Result:**
   - Welcome message lists all pending decisions (up to 5)
   - Each decision shows:
     - Decision ID
     - Decision text
     - Current vote counts
     - Votes needed for approval
     - Proposer name
   - Voting instructions are included

## Test Scenario 4: Existing Decision Thresholds Preserved

### Setup
1. Note the current channel member count
2. Create a pending decision (note its `approval_threshold`)
3. Have the decision receive 1-2 votes (but not enough to pass)

### Test Steps
1. Have a new user join the channel
2. Check the decision details:
   ```
   /decision show [decision_id]
   ```

3. **Expected Result:**
   - The `approval_threshold` remains unchanged
   - The `group_size_at_creation` remains unchanged
   - New member can still vote on the decision
   - Decision status updates correctly when threshold is met

## Test Scenario 5: Multiple Members Join Sequentially

### Setup
1. Create a pending decision
2. Have 2-3 users ready to join the channel

### Test Steps
1. Have first user join
2. Wait 2-3 seconds
3. Have second user join
4. Wait 2-3 seconds
5. Have third user join

6. **Expected Result:**
   - Each user receives their own welcome message
   - All welcome messages are delivered successfully
   - Server logs show all join events
   - No race conditions or errors
   - All new members can vote

## Verification Checklist

After running all tests, verify:

- ✅ New members receive welcome messages
- ✅ Welcome messages are ephemeral (only visible to the new member)
- ✅ Pending decisions are listed correctly
- ✅ Voting instructions are clear
- ✅ New members can vote on existing decisions
- ✅ Existing decision thresholds don't change
- ✅ No pending decisions scenario works correctly
- ✅ Multiple pending decisions are displayed
- ✅ Join events are logged
- ✅ No errors in server logs
- ✅ Multiple joins are handled correctly

## Common Issues and Solutions

### Issue: Welcome message not received
**Solution:**
- Check server logs for errors
- Verify bot has `chat:write` permission
- Verify `member_joined_channel` event is subscribed in Slack app settings
- Check that ngrok tunnel is active and webhook URL is correct

### Issue: "account_inactive" error
**Solution:**
- This means the Slack bot token is for an inactive workspace
- Reinstall the app to the workspace
- Update the `SLACK_BOT_TOKEN` in `.env`

### Issue: User info not found
**Solution:**
- Verify bot has `users:read` permission
- Check that the user ID is valid
- Welcome message will still be sent with "New Member" as fallback name

### Issue: No pending decisions shown when there are some
**Solution:**
- Check database connection
- Verify decisions are in "pending" status
- Check that channel_id matches
- Review server logs for database errors

## Server Log Examples

### Successful Member Join:
```
[2025-11-25 11:15:30] INFO - 📥 Received member_joined_channel event for user U12345 in channel C67890
[2025-11-25 11:15:30] INFO - 👋 Member John Doe (U12345) joined channel C67890
[2025-11-25 11:15:30] INFO - ✅ Sent welcome message to John Doe with 2 pending decisions
```

### Member Join with No Pending Decisions:
```
[2025-11-25 11:20:15] INFO - 📥 Received member_joined_channel event for user U54321 in channel C67890
[2025-11-25 11:20:15] INFO - 👋 Member Jane Smith (U54321) joined channel C67890
[2025-11-25 11:20:15] INFO - ✅ Sent welcome message to Jane Smith with 0 pending decisions
```

### Error Example:
```
[2025-11-25 11:25:00] ERROR - ❌ Error sending welcome message to John Doe: account_inactive
```
