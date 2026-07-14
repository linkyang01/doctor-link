# Failure-mode validation

Passed: 6/6

- PASS `multi_file_verified_repair` expected=verified actual=verified
- PASS `wrong_ai_fix_returns_failed` expected=failed actual=failed
- PASS `multi_file_hash_protection` expected=blocked actual=blocked
- PASS `allow_verification_changes_review_required` expected=review_required actual=review_required
- PASS `off_by_one_assist_reproduction` expected=reproduced actual=reproduced
- PASS `public_nodejs_corpus_pins` expected=present actual=present
