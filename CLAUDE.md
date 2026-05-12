# Git 규칙

## 브랜치 병합 전략

- `git push` 전 브랜치 통합 시 **rebase 대신 merge를 사용**한다.
  - `git pull --rebase` 대신 `git pull` (merge 방식) 사용
  - PR/브랜치 통합 시 rebase 없이 merge commit 생성
