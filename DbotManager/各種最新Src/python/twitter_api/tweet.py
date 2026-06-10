import json
from typing import Optional

from curl_cffi.requests import AsyncSession

from twitter_api.twitter_api import TwitterAPI


class Tweeter(TwitterAPI):
    """ツイート投稿機能を追加したTwitterAPIクラス。"""

    def _build_tweet_diagnostics(
        self,
        text: str,
        image_path: Optional[str],
        media_entities: list,
        image_upload_failed: bool,
    ) -> dict:
        text_len = len(text)
        diagnostics = {
            "text_length": text_len,
            "utf8_bytes": len(text.encode("utf-8")),
            "line_count": text.count("\n") + 1 if text else 0,
            "has_url": "http://" in text or "https://" in text,
            "has_hashtag": "#" in text,
            "has_mention": "@" in text,
            "has_image": bool(image_path),
            "image_path": image_path,
            "media_count": len(media_entities),
            "media_ids": [item.get("media_id") for item in media_entities],
            "image_upload_failed": image_upload_failed,
            "over_280_chars": text_len > 280,
            "empty_text": not bool(text),
        }

        reasons = []
        if diagnostics["over_280_chars"]:
            reasons.append("文字数が280文字を超えています")
        if diagnostics["empty_text"] and not diagnostics["has_image"]:
            reasons.append("本文も画像もありません")
        if diagnostics["has_image"] and diagnostics["image_upload_failed"]:
            reasons.append("画像アップロードに失敗し、文章のみ投稿に切り替えました")
        if diagnostics["line_count"] >= 8:
            reasons.append("改行が多い投稿です")
        diagnostics["reason_candidates"] = reasons
        return diagnostics

    def _format_tweet_diagnostics(self, diagnostics: dict) -> str:
        parts = [
            f"chars={diagnostics.get('text_length')}",
            f"bytes={diagnostics.get('utf8_bytes')}",
            f"lines={diagnostics.get('line_count')}",
            f"image={diagnostics.get('has_image')}",
            f"media_count={diagnostics.get('media_count')}",
        ]
        reasons = diagnostics.get("reason_candidates") or []
        if reasons:
            parts.append("candidates=" + " / ".join(reasons))
        return ", ".join(parts)

    async def post_tweet(
        self,
        text: str,
        session: AsyncSession,
        reply_to_tweet_id: Optional[str] = None,
        referer: str = "https://x.com/home",
        image_path: Optional[str] = None,
    ) -> bool:
        """ツイートを投稿する。返信と画像添付にも対応。"""
        if self.is_paused():
            return False

        text = (text or "").strip()
        if not text and not image_path:
            print("[ERROR] Tweet text or image_path is required.")
            return False

        url = "https://x.com/i/api/graphql/H-t2v_HvFR07ZBP9aOeKoA/CreateTweet"

        media_entities = []
        image_upload_failed = False
        if image_path:
            media_id = await self.upload_media(image_path, session)
            if media_id:
                media_entities.append({
                    "media_id": media_id,
                    "tagged_users": []
                })
            else:
                image_upload_failed = True
                print("[WARN] Image upload failed, posting text-only tweet.")

        diagnostics = self._build_tweet_diagnostics(
            text,
            image_path,
            media_entities,
            image_upload_failed,
        )
        self.last_tweet_diagnostics = diagnostics
        print(f"[TWEET_DIAG] {self._format_tweet_diagnostics(diagnostics)}")
        if diagnostics["over_280_chars"]:
            print("[WARN] Tweet text is over 280 characters. X may reject it.")

        variables = {
            "tweet_text": text,
            "media": {
                "media_entities": media_entities,
                "possibly_sensitive": False
            },
            "semantic_annotation_ids": [],
            "disallowed_reply_options": None,
            "semantic_annotation_options": {
                "source": "Htl"
            }
        }

        if reply_to_tweet_id:
            variables["reply"] = {
                "in_reply_to_tweet_id": reply_to_tweet_id,
                "exclude_reply_user_ids": []
            }
            if "status" not in referer:
                referer = f"https://x.com/i/status/{reply_to_tweet_id}"

        features = {
            "premium_content_api_read_enabled": False,
            "communities_web_enable_tweet_community_results_fetch": True,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
            "responsive_web_grok_analyze_post_followups_enabled": True,
            "rweb_cashtags_composer_attachment_enabled": True,
            "responsive_web_jetfuel_frame": True,
            "responsive_web_grok_share_attachment_enabled": True,
            "responsive_web_grok_annotations_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "rweb_conversational_replies_downvote_enabled": False,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "content_disclosure_indicator_enabled": True,
            "content_disclosure_ai_generated_indicator_enabled": True,
            "responsive_web_grok_show_grok_translated_post": True,
            "responsive_web_grok_analysis_button_from_backend": True,
            "post_ctas_fetch_enabled": False,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": False,
            "profile_label_improvements_pcf_label_in_post_enabled": True,
            "responsive_web_profile_redirect_enabled": False,
            "rweb_tipjar_consumption_enabled": False,
            "verified_phone_label_enabled": False,
            "articles_preview_enabled": True,
            "rweb_cashtags_enabled": True,
            "responsive_web_grok_community_note_auto_translation_is_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "responsive_web_grok_image_annotation_enabled": True,
            "responsive_web_grok_imagine_annotation_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True
        }

        payload = json.dumps({
            "variables": variables,
            "features": features,
            "queryId": "H-t2v_HvFR07ZBP9aOeKoA"
        }, separators=(",", ":"))

        print("[Processing] Generating TID via Node.js for CreateTweet...")
        tid = await self._generate_dynamic_transaction_id(
            "/i/api/graphql/H-t2v_HvFR07ZBP9aOeKoA/CreateTweet",
            "POST"
        )

        result = await self._execute_via_native_curl(
            url,
            payload,
            referer,
            '"rest_id"',
            tid
#            , session
        )
        if result["cookies"]:
            for key, value in result["cookies"].items():
                session.cookies.set(key, value, domain=".x.com")
        if not result["success"]:
            diag_summary = self._format_tweet_diagnostics(diagnostics)
            current_summary = getattr(self, "last_error_summary", None) or "投稿失敗"
            self.last_error_summary = f"{current_summary} | diag: {diag_summary}"
        return result["success"]
