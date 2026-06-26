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
- **Creating a group:** The bot owns the group and is automatically present. Do NOT add the bot as a member via the members API—it returns HTTP 400.
- **Member add scope:** Only add human members (by open_id). The chat owner (admin) is already in the group after creation, no need to add them.
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

- Add members body (omit bot and admin):

```json
{"id_list": ["<colleague_1_open_id>", "<colleague_2_open_id>"], "id_type": "open_id"}
```

- **Welcome card:** After creating the group and adding members, send an interactive card as a welcome message. Use `header.template = "blue"`, describe the bot's capabilities, list members.

## Urgent alert simulation card
Use an interactive card with `header.template = "red"`, explicit `[演练]` wording, and a note saying it is not a real incident. This gives the user the notification/card experience without causing real operational confusion.

## Credential parsing pitfall
Generated Feishu scripts should parse `.env` with a line-based `load_env_key()` helper, not regexes near `FEISHU_APP_SECRET`; inline regex patterns can be mangled by secret redaction.
