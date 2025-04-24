
# 🔀 Git 브랜치 전략 (IRKE BIM 개발용)

## 📌 브랜치 용도 정의

| 브랜치 이름      | 용도 설명 |
|------------------|-----------|
| `main`           | ✅ **배포용**: 항상 안정화된 상태로 유지. |
| `dev`            | 🛠️ **개발용**: VSCode에서 기본 작업 브랜치. 모든 기능은 이 브랜치로 병합됨. |
| `feature/***`    | ✨ **신규 기능 개발용**: `operator_***.py` 같은 새로운 기능 추가 시 사용. |
| `fix/***`        | 🐛 **버그 수정용**: 특정 기능의 버그 수정. 테스트 중 발견된 에러 처리용. |

---

## 🚀 브랜치 활용 시나리오

### ✅ 신규 기능 개발부터 배포까지의 예시 (view_operator.py 개발)

1. **신규 기능 개발 시작**  
   ```
   git checkout -b feature/view
   ```
   > `operator_view.py` 등 새 기능 파일 개발 시작

2. **테스트 중 에러 발생**

3. **버그 수정 브랜치 생성 및 병합**  
   ```
   git checkout -b fix/view
   git merge feature/view
   ```
   > 버그 수정 전용 브랜치에서 수정 작업 시작

4. **에러 수정 완료 후 기능 브랜치로 병합**  
   ```
   git checkout feature/view
   git merge fix/view
   ```

5. **최종 확인 후 기능 개발 완료**  
   > `view_operator.py` 정상 작동 확인

6. **개발 브랜치(dev)로 병합**  
   ```
   git checkout dev
   git merge feature/view
   ```

7. **배포 준비 완료 시 main 브랜치로 병합**  
   ```
   git checkout main
   git merge dev
   ```

---

## 🔁 병합 순서 요약

```
feature/view → fix/view → feature/view → dev → main
```

---

## 🧠 참고 사항
- `main`은 직접 작업하지 않고 **오직 병합만 허용**
- 병합 전에 항상 `pull`, 병합 후에는 `push`
- 충돌 발생 시 반드시 **수정 후 커밋**, 그리고 `push`
