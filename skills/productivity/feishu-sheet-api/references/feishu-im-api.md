# Feishu IM API: Groups, Members, and Messages

## Trigger
Use this when creating a Feishu group, adding approved users/colleagues, sending cards, or testing urgent alert cards.

## Key endpoints
- Tenant token: `POST /auth/v3/tenant_access_token/internal`
- Bot info: `GET /bot/v3/info`
- User info by user_id: `GET /contact/v3/users/{user_id}?user_id_type=user_id`
- Create group: `POST /im/v1/chats`
- Add members: `POST /im/v1/chats/{chat_id}/members`
- Send message/card: `POST /im/v1/messages?receive_id_type=chat_id`

## Practical notes
- Pairing IDs like `14b3e8ga` and `d93272ec` are Feishu `user_id` values. Convert them to `open_id` with `contact/v3/users/{user_id}?user_id_type=user_id` before adding to chats.
- The bot's own `open_id` comes from `/bot/v3/info`.
- Creating a group with the bot app may put the bot in the group automatically. Adding the bot again via the members API can return HTTP 400. Add human members first; verify bot presence through actual message send or chat info.
- For `im/v1/chats` group creation, a working body shape is:

```json
{
  "name": "网络团队 · Hermes 助手",
  "description": "内部 Hermes AI 助手群",
  "chat_mode": "group",
  "chat_type": "private",
  "owner_id": "<admin_open_id>",
  "join_message_visibility": "all_members",
  "leave_message_visibility": "all_members",
  "membership_approval": "no_approval_required"
}
```

- Add members body:

```json
{"id_list": ["<open_id_1>", "<open_id_2>"], "id_type": "open_id"}
```

## Urgent alert simulation card
Use an interactive card with `header.template = "red"`, explicit `[演练]` wording, and a note saying it is not a real incident. This gives the user the notification/card experience without causing real operational confusion.

## Credential parsing pitfall
Generated Feishu scripts should parse `.env` with a line-based `load_env_key()` helper, not regexes near `FEISHU_APP_SECRET`; inline regex patterns can be mangled by secret redaction.
