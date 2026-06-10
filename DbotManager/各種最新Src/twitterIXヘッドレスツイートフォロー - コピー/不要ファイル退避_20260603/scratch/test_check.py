from check_full_status import XRotatingScannerV410
import json

scanner = XRotatingScannerV410()
res = scanner.check_user("Yolanda79474127")
print(json.dumps(res, ensure_ascii=False))
