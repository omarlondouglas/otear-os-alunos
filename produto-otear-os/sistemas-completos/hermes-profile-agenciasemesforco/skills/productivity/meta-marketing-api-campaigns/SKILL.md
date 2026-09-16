---
name: meta-marketing-api-campaigns
description: Use when creating Meta Marketing API ad campaigns.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
      - meta-ads
      - marketing-api
      - facebook-ads
      - instagram-ads
      - whatsapp-ads
    related_skills: []
---

# Meta Marketing API Campaign Creation

## When to Use

Use this skill when the user asks to create, plan, debug, or explain Meta/Facebook/Instagram ads through the Marketing API.

## Core object hierarchy

1. **Campaign**: strategic objective and global status.
2. **Ad set**: budget, schedule, bidding, optimization, placement, audience targeting, promoted object.
3. **Ad creative**: visual/text asset and destination/call-to-action spec.
4. **Ad**: connects an ad set to a creative and sets final delivery status.

Default safe creation pattern: create all objects as `PAUSED`, verify them with GET calls, preview creatives when possible, then only publish with explicit user approval by setting ad/campaign/ad set to `ACTIVE`.

## Base endpoints

Graph version from provided docs: `v25.0`.

- Create campaign: `POST https://graph.facebook.com/v25.0/act_<AD_ACCOUNT_ID>/campaigns`
- Create ad set: `POST https://graph.facebook.com/v25.0/act_<AD_ACCOUNT_ID>/adsets`
- Create creative: `POST https://graph.facebook.com/v25.0/act_<AD_ACCOUNT_ID>/adcreatives`
- Create ad: `POST https://graph.facebook.com/v25.0/act_<AD_ACCOUNT_ID>/ads`
- Read/update object: `GET`/`POST https://graph.facebook.com/v25.0/<OBJECT_ID>`
- Insights: `GET https://graph.facebook.com/v25.0/<AD_ACCOUNT_ID|CAMPAIGN_ID|AD_SET_ID|AD_ID>/insights`
- Preview: `GET https://graph.facebook.com/v25.0/act_<AD_ACCOUNT_ID>/generatepreviews`

Always include `access_token`. Prefer JSON payloads for complex nested structures; `curl -F` is OK for simple forms.

## Required access and prerequisites

For most creation tasks:

- Valid Meta ad account: `act_<AD_ACCOUNT_ID>`.
- Access token with `ads_management`; insights need `ads_read` or `ads_management`.
- For messaging ads: Page access token requested by a user with Page ADVERTISE task.
- Common messaging permissions: `ads_management`, `pages_manage_ads`, `pages_read_engagement`, `pages_show_list`.
- Facebook Page ID for promoted object and creative.
- Uploaded asset IDs/hashes for images/videos where required.
- Instagram account connected when using Instagram Direct destination.
- WhatsApp business number connected to Page when using WhatsApp destination.
- `special_ad_categories` is required for newer campaign creation; use `[]`/`NONE` only if legally correct.

## Basic campaign creation

Campaign required fields:

- `name`
- `objective`
- `status` (`PAUSED` safest)
- For messaging docs, `special_ad_categories` is required.

Example:

```bash
curl -X POST \
  -F 'name=My Campaign' \
  -F 'objective=OUTCOME_TRAFFIC' \
  -F 'status=PAUSED' \
  -F 'special_ad_categories=[]' \
  -F 'access_token=<ACCESS_TOKEN>' \
  https://graph.facebook.com/v25.0/act_<AD_ACCOUNT_ID>/campaigns
```

Legacy/basic docs show `LINK_CLICKS`; messaging campaign docs use outcome objectives such as `OUTCOME_ENGAGEMENT`, `OUTCOME_LEADS`, `OUTCOME_SALES`, `OUTCOME_TRAFFIC`.

## Basic ad set creation

Ad set usually needs:

- `name`
- `campaign_id`
- `daily_budget` or `lifetime_budget` (`lifetime_budget` requires end time)
- `targeting`
- `billing_event`
- `optimization_goal`
- `status`
- For messaging ads: `destination_type` and `promoted_object.page_id`

Example general ad set:

```bash
curl -X POST \
  -F 'name=My Ad Set' \
  -F 'campaign_id=<CAMPAIGN_ID>' \
  -F 'daily_budget=1000' \
  -F 'targeting={"geo_locations":{"countries":["US"]}}' \
  -F 'optimization_goal=LINK_CLICKS' \
  -F 'billing_event=IMPRESSIONS' \
  -F 'status=PAUSED' \
  -F 'access_token=<ACCESS_TOKEN>' \
  https://graph.facebook.com/v25.0/act_<AD_ACCOUNT_ID>/adsets
```

Placement targeting belongs in ad set `targeting`/target spec, e.g. `publisher_platforms`, `device_platforms`. Leaving placement unspecified allows Meta delivery optimization across placements.

## Basic creative creation

A creative defines what the ad renders. Common field:

- `name`
- `object_story_spec`

Simple link creative:

```bash
curl -X POST \
  -F 'name=Sample Creative' \
  -F 'object_story_spec={
    "page_id":"<PAGE_ID>",
    "link_data":{
      "message":"Check out our new product!",
      "link":"https://example.com/product",
      "caption":"Our New Product",
      "picture":"https://example.com/image.jpg",
      "call_to_action":{"type":"SHOP_NOW"}
    }
  }' \
  -F 'access_token=<ACCESS_TOKEN>' \
  https://graph.facebook.com/v25.0/act_<AD_ACCOUNT_ID>/adcreatives
```

For promoted Page posts, use `object_story_id` in format `<PAGE_ID>_<POST_ID>`.

If Meta returns `Creative Must Provide enroll_status for Standard Enhancements`, add:

```json
"degrees_of_freedom_spec": {
  "creative_features_spec": {
    "standard_enhancements": {"enroll_status": "OPT_IN"}
  }
}
```

Use `OPT_OUT` only if the strategy requires disabling standard enhancements.

## Basic ad creation

Required:

- `name`
- `adset_id`
- `creative` containing `creative_id`
- `status`

```bash
curl -X POST \
  -F 'name=My Ad' \
  -F 'adset_id=<AD_SET_ID>' \
  -F 'creative={"creative_id":"<CREATIVE_ID>"}' \
  -F 'status=PAUSED' \
  -F 'access_token=<ACCESS_TOKEN>' \
  https://graph.facebook.com/v25.0/act_<AD_ACCOUNT_ID>/ads
```

To publish after approval from user:

```bash
curl -X POST \
  -F 'status=ACTIVE' \
  -F 'access_token=<ACCESS_TOKEN>' \
  https://graph.facebook.com/v25.0/<AD_ID>
```

After publishing, effective status may become `PENDING_REVIEW` until Meta approves.

## Click-to-WhatsApp ads

Campaign:

- Objectives supported: `OUTCOME_ENGAGEMENT`, `OUTCOME_LEADS`, `OUTCOME_SALES`, `OUTCOME_TRAFFIC`.
- Campaigns with call prompts must use `OUTCOME_ENGAGEMENT`.
- Include `special_ad_categories=[]` if applicable.

Ad set:

- `destination_type=WHATSAPP`
- `billing_event=IMPRESSIONS`
- `optimization_goal`: depends on campaign objective; common `CONVERSATIONS`, `LINK_CLICKS`, or `IMPRESSIONS` depending setup.
- `promoted_object={"page_id":"<PAGE_ID>"}`; optional `whatsapp_phone_number`.
- Targeting should generally include mobile if optimizing WhatsApp conversations.

Creative:

- `object_story_spec.page_id` required.
- `link_data.link` often `api.whatsapp.com/send`.
- CTA:

```json
"call_to_action": {
  "type": "WHATSAPP_MESSAGE",
  "value": {"app_destination": "WHATSAPP"}
}
```

Can add `page_welcome_message` under `link_data` with `VISUAL_EDITOR`, `version:2`, `landing_screen_type`, and either autofill messages, icebreakers, call prompt, website/catalog CTA, or eligible WhatsApp Flow.

WhatsApp Flow constraints from docs:

- Flow version > 5.1
- No validation errors
- Static flow, single screen
- Eligible components only
- Max 8 components
- At least one input component
- Flow belongs to same WhatsApp Business Account as promoted number.

## Click-to-Instagram Direct ads

Campaign:

- Supported objectives: `OUTCOME_ENGAGEMENT`, `OUTCOME_SALES`, `OUTCOME_TRAFFIC`.

Ad set:

- `destination_type=INSTAGRAM_DIRECT`
- `billing_event=IMPRESSIONS`
- `optimization_goal=CONVERSATIONS` is common for chat campaigns.
- `promoted_object={"page_id":"<PAGE_ID>"}`.

Creative:

- `object_story_spec.page_id`
- `object_story_spec.instagram_actor_id` for account-backed creative, or `instagram_user_id` in post-as-ad flows.
- CTA:

```json
"call_to_action": {
  "type": "INSTAGRAM_MESSAGE",
  "value": {"app_destination": "INSTAGRAM_DIRECT"}
}
```

Can use image, video, carousel, or existing Instagram content (`source_instagram_media_id`).

Welcome message supports icebreakers with optional responses. Limits from multidestination docs: icebreaker titles <= 80 chars, responses <= 300 chars, message text <= 300 chars.

## Click-to-multidestination ads

Use when Meta should route to the messaging app most likely to get a response.

Campaign:

- Supported objectives: `OUTCOME_ENGAGEMENT`, `OUTCOME_SALES`, `OUTCOME_TRAFFIC`.
- `special_ad_categories` should be empty/NONE only where legally correct.

Ad set:

- `optimization_goal=CONVERSATIONS` required.
- `billing_event=IMPRESSIONS`.
- `destination_type` must match destinations:
  - `MESSAGING_INSTAGRAM_DIRECT_MESSENGER_WHATSAPP`
  - `MESSAGING_INSTAGRAM_DIRECT_MESSENGER`
  - `MESSAGING_MESSENGER_WHATSAPP`
  - `MESSAGING_INSTAGRAM_DIRECT_WHATSAPP`
- Ensure Page has required Instagram and/or WhatsApp connections.

Creative:

- Requires `asset_feed_spec.optimization_type=DOF_MESSAGING_DESTINATION`.
- `asset_feed_spec.call_to_actions` must match ad set destination set.

CTA snippets:

Messenger:
```json
{"type":"MESSAGE_PAGE","value":{"app_destination":"MESSENGER","link":"fb.com/messenger_doc"}}
```

WhatsApp:
```json
{"type":"WHATSAPP_MESSAGE","value":{"app_destination":"WHATSAPP","link":"api.whatsapp.com/send"}}
```

Instagram:
```json
{"type":"INSTAGRAM_MESSAGE","value":{"app_destination":"INSTAGRAM_DIRECT","link":"instagram.com"}}
```

## Using existing Instagram/Facebook posts as ads

Instagram posts:

1. Get IG User ID via Page `instagram_business_account`, ad account `connected_instagram_accounts`, or business `instagram_business_accounts`.
2. Find media via IG Graph API media/stories endpoint.
3. Check `boost_eligibility_info`.
4. Create creative with `object_id`/`instagram_user_id`/`source_instagram_media_id` and CTA.

Limitations:

- Copyrighted music or interactive elements like filters may not be boostable.
- Instagram TV posts not supported.

Facebook posts as Instagram ads:

- Check `is_instagram_eligible` on the post.
- Use `object_story_id=<postOwnerID_postID>` and `instagram_user_id`/`instagram_actor_id`.

If using Facebook post + Instagram user + Facebook and Instagram placements, errors like “Creative is missing DOF spec” require `asset_feed_spec.optimization_type=DOF_MESSAGING_DESTINATION`.

## Video ads upload flow

Permissions:

- `ads_read`
- `ads_management`
- User must be able to perform `CREATE_CONTENT` on ad account.
- Uploading videos to business accounts is not supported; upload to ad accounts only.

Video specs:

- MP4 recommended.
- Aspect ratio 16:9 to 9:16.
- Recommended max size up to 10GB.
- Minimum width 1200px, recommended 1280x720.
- 24–60 fps.
- H.264/H.265 recommended; progressive scan; fixed frame rate; AAC LC stereo 48kHz 128kbps+.

Flow:

1. Initialize: `POST /act_<PAYMENT_ACCOUNT_ID>/video_ads` with `upload_phase=start`.
2. Upload to returned `upload_url` on `rupload.facebook.com/video-ads-upload/v25.0/<VIDEO_ID>` with headers:
   - `Authorization: OAuth <ACCESS_TOKEN>`
   - `offset: 0` or resume offset
   - `file_size: <bytes>` for local upload, or `file_url: <public_url>` for hosted file.
3. Optional status: `GET /<VIDEO_ID>?fields=status`.
4. Finish/publish video to ad account: `POST /act_<PAYMENT_ACCOUNT_ID>/video_ads` with `upload_phase=finish` and `video_id`.

For interrupted upload, read `status.uploading_phase.bytes_transferred` and resume from that offset.

## Insights and optimization

Insights endpoint can be called from ad account, campaign, ad set, or ad:

```bash
curl -G \
  -d 'fields=impressions,clicks,spend' \
  -d 'time_range={"since":"2026-01-01","until":"2026-01-31"}' \
  -d 'access_token=<ACCESS_TOKEN>' \
  https://graph.facebook.com/v25.0/act_<AD_ACCOUNT_ID>/insights
```

For Facebook/Instagram placement breakdown:

- Use `breakdowns=publisher_platform,platform_position` (docs include one typo as `breakdown`; prefer official plural `breakdowns`).
- Instagram placement values include `feed`, `instagram_explore`, `instagram_reels`, `instagram_stories`.

Key fields to request depending on goal:

- Delivery/spend: `impressions`, `reach`, `frequency`, `spend`
- Traffic: `clicks`, `inline_link_clicks`, `ctr`, `cpc`, `outbound_clicks`
- Messaging/leads/sales: include actions/action_values fields if available for account setup.

Optimization habits:

- Use custom audiences for warm audiences.
- Segment by demographics/location/interests when useful.
- Use lookalikes from best customers.
- Monitor and shift budget to best-performing ads/ad sets.
- A/B test creatives, headlines, hooks, and CTAs.
- Consider dynamic creatives / Advantage+ creative enhancements.
- Use Conversions API when optimizing for downstream business outcomes.
- Add URL tags/UTMs; for placement tracking use macros like `SITE_SOURCE_NAME` where supported.

## Preview and verification

Preview by creative spec or creative ID:

```bash
curl -G \
  --data-urlencode 'creative={"object_story_id":"<PAGE_ID>_<POST_ID>"}' \
  -d 'ad_format=DESKTOP_FEED_STANDARD' \
  -d 'access_token=<ACCESS_TOKEN>' \
  https://graph.facebook.com/v25.0/act_<AD_ACCOUNT_ID>/generatepreviews
```

Preview iframe is valid for 24 hours.

Verification reads:

- Campaign: `fields=name,status,objective`
- Ad set: `fields=name,destination_type,optimization_goal,bid_strategy,status`
- Creative: `fields=name,object_story_spec{link_data{call_to_action,page_welcome_message}},asset_feed_spec`
- Ad: `fields=status,effective_status,adset_id,campaign_id`

## Management operations

Update any campaign/ad set/ad/creative with `POST /<OBJECT_ID>` and changed fields.

Status changes:

- Pause: `status=PAUSED`
- Resume/publish: `status=ACTIVE`
- Archive: `status=ARCHIVED`
- Delete: `DELETE /<OBJECT_ID>` (irreversible; ask explicit confirmation before deleting)

Be careful: pausing a campaign gives active child ad sets/ads an effective status like `CAMPAIGN_PAUSED`.

## Common pitfalls from provided docs

- Some snippets in docs omit slashes before object IDs (`v25.0<CAMPAIGN_ID>`). Correct form is usually `https://graph.facebook.com/v25.0/<OBJECT_ID>`.
- Some snippets contain syntax typos/missing commas or quotes; build JSON programmatically rather than copy-pasting unvalidated snippets.
- `daily_budget` is in the ad account currency’s minor unit/cents-style amount in many examples. Confirm currency/account rules before launch.
- Do not publish (`ACTIVE`) without explicit user approval and final preview/verification.
- For messaging ads, ensure `destination_type`, CTA, `asset_feed_spec`, Page/IG/WhatsApp connections, and `promoted_object` are consistent.
- For multidestination, `asset_feed_spec.call_to_actions` must match ad set `destination_type`.
- For post-as-ad, always check boost/Instagram eligibility first.
- Uploading video ads to business accounts is unsupported in provided docs; use ad account endpoint.

## Minimal safe workflow checklist

1. Collect: ad account ID, page ID, token, objective, destination, budget, geo/targeting, creative assets, copy, special category status.
2. Validate prerequisites/permissions and asset availability.
3. Create campaign as `PAUSED`.
4. Read campaign back.
5. Create ad set as `PAUSED` with targeting, budget, promoted object, optimization/billing/destination.
6. Read ad set back.
7. Create/upload assets if needed; for video, complete video upload flow first.
8. Create creative with correct CTA and optional welcome message/icebreakers.
9. Read creative back and generate previews.
10. Create ad as `PAUSED`.
11. Read ad back.
12. Ask user for explicit approval to publish.
13. Set status `ACTIVE` and verify `status`/`effective_status`.
14. Monitor insights and optimize.
