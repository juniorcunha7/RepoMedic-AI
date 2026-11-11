# Boundary-condition defect

Expected free shipping when `total >= threshold`.

| Total | Expected | Original result | Patched result |
|---|---|---|---|
| $49.99 | no | no | no |
| $50.00 | yes | no | yes |
| $50.01 | yes | yes | yes |

The intentionally defective code is packaged as a *string fixture* in `repomedic/fixture.py`. It is copied into a temporary working folder for tests, without editing any user's repository.
