"""
Report 2 - 동치 관계 판별 및 동치류 출력 프로그램
================================================
집합 A = {1, 2, 3, 4, 5} 에 관한 관계행렬을 입력받아
  1) 관계행렬 입력      : 5 x 5 행렬을 행 단위로 입력받아 2차원 리스트로 저장
  2) 동치 관계 판별     : 반사 / 대칭 / 추이 관계를 각각 판별하고 결과 메시지 출력
  3) 동치류 출력        : 동치 관계이면 각 원소의 동치류 [a] 를 출력
  4) 폐포 구현          : 성질을 만족하지 않으면 반사/대칭/추이 폐포로 변환하고
                          변환 전/후 출력 -> 다시 판별 -> 동치류 출력
[추가 기능]
  - 입력 오류 검증 및 재입력 (개수, 0/1 이외의 값, 공백 없는 입력 허용)
  - 성질을 만족하지 않는 근거(반례) 순서쌍 출력
  - 관계를 순서쌍 집합으로 표기, 동치류가 A 의 분할(A/R)인지 검증
  - 메뉴 (직접 입력 / 예제 선택 / 무작위 생성) 와 반복 실행
  - 관계 방향그래프 시각화 이미지 저장 (matplotlib, networkx 설치 시)

실행 : python equivalence_relation.py          (색상 끄기: --no-color, 그래프 끄기: --no-graph)
"""

import os
import random
import sys
import unicodedata

N = 5                          # 집합의 원소 개수
A = list(range(1, N + 1))      # 집합 A = {1, 2, 3, 4, 5}

# ---------------------------------------------------------------------------
# 출력 보조 함수 (터미널 색상, 한글 폭 맞춤)
# ---------------------------------------------------------------------------
if os.name == "nt":            # Windows 터미널에서 ANSI 색상 활성화
    os.system("")
USE_COLOR = "--no-color" not in sys.argv
DRAW_GRAPH = "--no-graph" not in sys.argv
STEP_MODE = "--no-pause" not in sys.argv      # 단계별 일시정지 (화면을 단계마다 나눠서 보기)


def color(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


def green(t):  return color(t, "1;32")
def red(t):    return color(t, "1;31")
def yellow(t): return color(t, "1;33")
def cyan(t):   return color(t, "1;36")
def bold(t):   return color(t, "1")


def width(s):
    """한글(전각 문자)은 2칸으로 계산한 화면 출력 폭"""
    return sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in s)


def pad(s, w):
    return s + " " * max(0, w - width(s))


def line(ch="=", n=60):
    print(cyan(ch * n))


def next_step(label):
    """[추가 기능] 단계별 실행 : Enter 를 누르면 화면을 지우고 다음 단계로 진행"""
    if not STEP_MODE:
        return
    input(cyan(f"\n  [Enter] 다음 단계 ▶ {label} "))
    print("\033[2J\033[3J\033[H", end="")     # 터미널 화면 지우기


def set_str(s):
    """집합을 {1, 2, 3} 형태의 문자열로"""
    return "{" + ", ".join(str(x) for x in sorted(s)) + "}"


# ---------------------------------------------------------------------------
# [조건 1] 관계행렬 입력 기능
# ---------------------------------------------------------------------------
def parse_row(text):
    """한 행의 입력 문자열을 0/1 리스트로 변환 (오류 시 ValueError)"""
    text = text.strip().replace(",", " ")
    tokens = text.split()
    if len(tokens) == 1 and len(tokens[0]) == N:      # '10100' 처럼 공백 없이 입력한 경우
        tokens = list(tokens[0])
    if len(tokens) != N:
        raise ValueError(f"값을 {N}개 입력해야 합니다. (입력한 개수: {len(tokens)})")
    row = []
    for t in tokens:
        if t not in ("0", "1"):
            raise ValueError(f"'{t}' 는 사용할 수 없습니다. 0 또는 1만 입력하세요.")
        row.append(int(t))
    return row


def input_matrix():
    """사용자로부터 5 x 5 관계행렬을 행 단위로 입력받아 2차원 리스트로 반환"""
    print(f"\n집합 A = {set_str(A)} 에 관한 {N} x {N} 관계행렬을 입력하세요.")
    print("각 행마다 0 또는 1을 공백으로 구분하여 입력합니다. (예: 1 0 1 0 0)")
    matrix = []                                   # 2차원 리스트(배열)
    for i in range(N):
        while True:                               # 올바르게 입력할 때까지 반복
            try:
                row = parse_row(input(f"  {i + 1}행 입력 > "))
                matrix.append(row)                # 한 행씩 리스트에 추가
                break
            except ValueError as e:
                print(red(f"  [입력 오류] {e} 다시 입력하세요."))
    return matrix


def print_matrix(M, title="관계행렬 M_R"):
    print(bold(f"\n  {title}"))
    print("       " + "  ".join(str(a) for a in A))
    print("     +" + "-" * (3 * N))
    for i in range(N):
        print(f"   {A[i]} | " + "  ".join(str(v) for v in M[i]))


def matrix_to_pairs(M):
    """관계행렬 -> 순서쌍 리스트 [(a, b), ...]"""
    return [(A[i], A[j]) for i in range(N) for j in range(N) if M[i][j] == 1]


def pairs_str(pairs):
    return "{" + ", ".join(f"({a},{b})" for a, b in pairs) + "}" if pairs else "{ } (공집합)"


# ---------------------------------------------------------------------------
# [조건 2] 동치 관계 판별 기능 - 반사, 대칭, 추이 판별 함수
# ---------------------------------------------------------------------------
def is_reflexive(M):
    """반사 관계 : 모든 a 에 대해 (a,a) ∈ R  <=>  주대각 원소가 모두 1"""
    for i in range(N):
        if M[i][i] != 1:
            return False
    return True


def is_symmetric(M):
    """대칭 관계 : (a,b) ∈ R 이면 (b,a) ∈ R  <=>  M[i][j] == M[j][i] (M = M^T)"""
    for i in range(N):
        for j in range(N):
            if M[i][j] != M[j][i]:
                return False
    return True


def is_transitive(M):
    """추이 관계 : (a,b) ∈ R 이고 (b,c) ∈ R 이면 (a,c) ∈ R"""
    for i in range(N):
        for j in range(N):
            if M[i][j] == 1:
                for k in range(N):
                    if M[j][k] == 1 and M[i][k] == 0:
                        return False
    return True


# [추가 기능] 성질을 만족하지 않는 근거(반례) 찾기 ---------------------------
def reflexive_violations(M):
    return [(A[i], A[i]) for i in range(N) if M[i][i] == 0]


def symmetric_violations(M):
    return [((A[i], A[j]), (A[j], A[i]))
            for i in range(N) for j in range(N) if M[i][j] == 1 and M[j][i] == 0]


def transitive_violations(M):
    result = []
    for i in range(N):
        for j in range(N):
            for k in range(N):
                if M[i][j] and M[j][k] and not M[i][k]:
                    result.append(((A[i], A[j]), (A[j], A[k]), (A[i], A[k])))
    return result


def ox(flag):
    return green("O (만족)") if flag else red("X (불만족)")


def check_equivalence(M, detail=True):
    """반사/대칭/추이 판별 결과를 출력하고 동치 관계 여부를 반환"""
    r, s, t = is_reflexive(M), is_symmetric(M), is_transitive(M)
    if detail:
        print(f"  - 반사 관계 : {ox(r)}")
        if not r:
            v = reflexive_violations(M)
            print(f"      근거: {', '.join(f'({a},{a})' for a, _ in v)} ∉ R")
        print(f"  - 대칭 관계 : {ox(s)}")
        if not s:
            v = symmetric_violations(M)
            print("      근거: " + ", ".join(f"({p[0]},{p[1]}) ∈ R 이지만 ({q[0]},{q[1]}) ∉ R"
                                         for p, q in v[:2]) + (f"  외 {len(v) - 2}건" if len(v) > 2 else ""))
        print(f"  - 추이 관계 : {ox(t)}")
        if not t:
            v = transitive_violations(M)
            p, q, x = v[0]
            print(f"      근거: ({p[0]},{p[1]}), ({q[0]},{q[1]}) ∈ R 이지만 ({x[0]},{x[1]}) ∉ R"
                  + (f"  외 {len(v) - 1}건" if len(v) > 1 else ""))
    else:
        print(f"반사 {'O' if r else 'X'} | 대칭 {'O' if s else 'X'} | 추이 {'O' if t else 'X'}")

    if r and s and t:
        print(green("  => 반사, 대칭, 추이 관계를 모두 만족하므로 동치 관계입니다."))
        return True
    missing = [name for name, ok in (("반사", r), ("대칭", s), ("추이", t)) if not ok]
    print(red(f"  => {', '.join(missing)} 관계를 만족하지 않으므로 동치 관계가 아닙니다."))
    return False


# ---------------------------------------------------------------------------
# [조건 3] 동치 관계일 경우 동치류 출력 기능
# ---------------------------------------------------------------------------
def equivalence_class(M, a):
    """원소 a 의 동치류 [a] = { x ∈ A | (a, x) ∈ R }"""
    i = A.index(a)
    return {A[j] for j in range(N) if M[i][j] == 1}


def print_equivalence_classes(M):
    print(bold("\n  [ 각 원소의 동치류 ]"))
    classes = []
    for a in A:
        c = equivalence_class(M, a)
        print(f"    [{a}] = {set_str(c)}")
        if c not in classes:
            classes.append(c)
    # [추가 기능] 서로 다른 동치류가 A 의 분할(partition)인지 검증
    union = set().union(*classes)
    disjoint = all(not (x & y) for i, x in enumerate(classes) for y in classes[i + 1:])
    print(bold("\n  [ 분할 A/R ]"))
    print(f"    A/R = {{ {', '.join(set_str(c) for c in classes)} }}  (동치류 {len(classes)}개)")
    print(f"    합집합 = A : {ox(union == set(A))},  서로소 : {ox(disjoint)}")
    return classes


# ---------------------------------------------------------------------------
# [조건 4] 폐포 구현 기능
# ---------------------------------------------------------------------------
def copy_matrix(M):
    return [row[:] for row in M]


def reflexive_closure(M):
    """반사 폐포 r(R) = R ∪ { (a,a) | a ∈ A } : 주대각 원소를 모두 1로"""
    C = copy_matrix(M)
    for i in range(N):
        C[i][i] = 1
    return C


def symmetric_closure(M):
    """대칭 폐포 s(R) = R ∪ R^-1 : M[i][j] 또는 M[j][i] 가 1이면 둘 다 1로"""
    C = copy_matrix(M)
    for i in range(N):
        for j in range(N):
            if M[i][j] == 1:
                C[j][i] = 1
    return C


def transitive_closure(M):
    """추이 폐포 t(R) : 와샬(Warshall) 알고리즘
    k 를 경유점으로 i -> k, k -> j 경로가 있으면 i -> j 를 추가"""
    C = copy_matrix(M)
    for k in range(N):
        for i in range(N):
            for j in range(N):
                if C[i][k] == 1 and C[k][j] == 1:
                    C[i][j] = 1
    return C


def print_before_after(before, after, left="변환 전", right="변환 후"):
    """변환 전/후 행렬을 나란히 출력하고 새로 추가된 원소를 표시"""
    col = 4 * N + 7
    print("\n    " + pad(left, col) + "      " + right)
    head = "      " + "".join(f"{a:>3} " for a in A)
    print("    " + pad(head, col) + "      " + head)
    for i in range(N):
        l = f"   {A[i]} |" + "".join(f"{v:>3} " for v in before[i])
        r = f"   {A[i]} |"
        for j in range(N):
            cell = f"{after[i][j]:>3}"
            if after[i][j] != before[i][j]:
                r += yellow(cell + "*")          # 폐포로 새로 추가된 원소
            else:
                r += cell + " "
        print("    " + pad(l, col) + "  ->  " + r)
    added = [(A[i], A[j]) for i in range(N) for j in range(N) if after[i][j] != before[i][j]]
    print(f"    추가된 순서쌍 ({len(added)}개, * 표시): " + (yellow(pairs_str(added)) if added else "없음"))
    return added


def process_closures(M):
    """성질을 만족하지 않으면 각각의 폐포로 변환 -> 변환 전/후 출력 -> 다시 판별 -> 동치류 출력"""
    line("-")
    print(bold("[4] 폐포 구현"))
    line("-")

    closures = [("반사", is_reflexive, reflexive_closure, "r(R)"),
                ("대칭", is_symmetric, symmetric_closure, "s(R)"),
                ("추이", is_transitive, transitive_closure, "t(R)")]

    # 4-1. 입력받은 관계 R 에 대해, 만족하지 않는 성질 각각의 폐포
    print(bold("\n 4-1. 성질별 폐포 (입력 관계 R 에 각각 적용)"))
    for name, check, closure, sym in closures:
        if check(M):
            print(f"\n  ■ {name} 관계를 이미 만족하므로 {name} 폐포는 R 자신입니다.")
            continue
        print(bold(f"\n  ■ {name} 폐포 {sym}"))
        C = closure(M)
        print_before_after(M, C, "변환 전 R", f"변환 후 {sym}")
        print(f"  {sym} 다시 판별 : ", end="")
        if check_equivalence(C, detail=False):
            print_equivalence_classes(C)

    next_step("4-2. 동치 폐포")
    # 4-2. 동치 폐포 : R -> 반사 폐포 -> 대칭 폐포 -> 추이 폐포 순서로 누적 적용
    print(bold("\n 4-2. 동치 폐포 (반사 -> 대칭 -> 추이 폐포를 차례로 적용)"))
    cur = copy_matrix(M)
    for step, (name, check, closure, sym) in enumerate(closures, 1):
        if check(cur):
            print(f"\n  [STEP {step}] {name} 관계를 이미 만족 -> 변환 생략")
            continue
        print(bold(f"\n  [STEP {step}] {name} 폐포 적용"))
        nxt = closure(cur)
        print_before_after(cur, nxt, "변환 전", f"{name} 폐포 적용 후")
        cur = nxt
        print("  다시 판별 : ", end="")
        check_equivalence(cur, detail=False)

    next_step("최종 관계 다시 판별")
    print(bold("\n  [ 최종 관계 다시 판별 ]"))
    print_matrix(cur, "동치 폐포 행렬")
    print(f"\n  순서쌍 : {pairs_str(matrix_to_pairs(cur))}")
    print()
    if check_equivalence(cur):
        print_equivalence_classes(cur)
    return cur


# ---------------------------------------------------------------------------
# [추가 기능] 예제 / 무작위 생성 / 그래프 시각화 / 메뉴
# ---------------------------------------------------------------------------
EXAMPLES = {
    "1": ("동치 관계 예제",
          [[1, 1, 0, 0, 0],
           [1, 1, 0, 0, 0],
           [0, 0, 1, 0, 0],
           [0, 0, 0, 1, 1],
           [0, 0, 0, 1, 1]]),
    "2": ("반사 X, 대칭 X, 추이 X 예제",
          [[1, 1, 0, 0, 0],
           [0, 0, 1, 0, 0],
           [0, 0, 0, 0, 0],
           [0, 0, 0, 1, 0],
           [0, 0, 0, 1, 0]]),
    "3": ("반사만 X 예제 (대칭 O, 추이 O)",
          [[1, 1, 0, 0, 0],
           [1, 1, 0, 0, 0],
           [0, 0, 0, 0, 0],
           [0, 0, 0, 1, 0],
           [0, 0, 0, 0, 0]]),
    "4": ("추이만 X 예제 (반사 O, 대칭 O)",
          [[1, 1, 0, 0, 0],
           [1, 1, 1, 0, 0],
           [0, 1, 1, 0, 0],
           [0, 0, 0, 1, 0],
           [0, 0, 0, 0, 1]]),
}


def choose_example():
    print()
    for key, (name, _) in EXAMPLES.items():
        print(f"  {key}. {name}")
    while True:
        key = input("  예제 번호 선택 > ").strip()
        if key in EXAMPLES:
            print(f"  '{EXAMPLES[key][0]}' 을(를) 불러왔습니다.")
            return copy_matrix(EXAMPLES[key][1])
        print(red("  [입력 오류] 목록에 있는 번호를 입력하세요."))


def random_matrix(p=0.3):
    """대각 원소는 50%, 나머지는 확률 p 로 1인 무작위 관계행렬"""
    return [[1 if random.random() < (0.5 if i == j else p) else 0 for j in range(N)]
            for i in range(N)]


def save_relation_graph(original, final, filename="relation_graph.png"):
    """원래 관계와 동치 폐포(또는 동치 관계)를 방향그래프로 나란히 저장"""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import networkx as nx
    except ImportError:
        print("  (matplotlib / networkx 가 설치되어 있지 않아 그래프 저장을 건너뜁니다.)")
        return None

    for f in ("Malgun Gothic", "AppleGothic", "NanumGothic", "Noto Sans CJK KR"):
        plt.rcParams["font.family"] = f
        from matplotlib import font_manager
        if any(f == x.name for x in font_manager.fontManager.ttflist):
            break
    plt.rcParams["axes.unicode_minus"] = False

    classes = []
    if is_reflexive(final) and is_symmetric(final) and is_transitive(final):
        for a in A:
            c = equivalence_class(final, a)
            if c not in classes:
                classes.append(c)
    palette = ["#4C9BE8", "#F2A541", "#5CC689", "#E0607E", "#A77BD9"]
    node_color = []
    for a in A:
        idx = next((k for k, c in enumerate(classes) if a in c), None)
        node_color.append(palette[idx % len(palette)] if idx is not None else "#BBBBBB")

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    pos = nx.circular_layout(range(1, N + 1))
    for ax, M, title in ((axes[0], original, "입력 관계 R"),
                         (axes[1], final, "결과 관계 (동치류별 색상)")):
        G = nx.DiGraph()
        G.add_nodes_from(A)
        edges = matrix_to_pairs(M)
        G.add_edges_from(edges)
        new = [e for e in edges if original[e[0] - 1][e[1] - 1] == 0]
        old = [e for e in edges if e not in new]
        colors = node_color if M is final else ["#BBBBBB"] * N
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colors, node_size=900, edgecolors="#333")
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=14, font_weight="bold")
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=old, arrowstyle="-|>", arrowsize=18,
                               node_size=900, connectionstyle="arc3,rad=0.12", edge_color="#333")
        nx.draw_networkx_edges(G, pos, ax=ax, edgelist=new, arrowstyle="-|>", arrowsize=18,
                               node_size=900, connectionstyle="arc3,rad=0.12",
                               edge_color="#E04040", style="dashed")
        ax.set_title(title, fontsize=14)
        ax.axis("off")
    fig.text(0.5, 0.02, "검은 실선: 기존 순서쌍   빨간 점선: 폐포로 추가된 순서쌍   (자기 루프 (a,a)는 노드 위 고리)",
             ha="center", fontsize=10)
    plt.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    return filename


def run(M):
    """입력된 관계행렬 하나에 대해 전체 과정 수행"""
    line()
    print(bold("[1] 입력된 관계행렬 (2차원 리스트로 저장됨)"))
    line()
    print_matrix(M)
    print(f"\n  리스트 저장 형태 : {M}")
    print(f"  순서쌍 표기 R = {pairs_str(matrix_to_pairs(M))}")

    line("-")
    print(bold("[2] 동치 관계 판별"))
    line("-")
    if check_equivalence(M):
        line("-")
        print(bold("[3] 동치류 출력"))
        line("-")
        print_equivalence_classes(M)
        final = M
    else:
        next_step("[4] 폐포 구현")
        final = process_closures(M)

    if DRAW_GRAPH:
        path = save_relation_graph(M, final)
        if path:
            print(f"\n  [그래프] 관계 방향그래프를 '{path}' 파일로 저장했습니다.")


def main():
    line()
    print(bold("   동치 관계 판별 및 동치류 출력 프로그램   (A = {1, 2, 3, 4, 5})"))
    line()
    while True:
        print("\n  1. 관계행렬 직접 입력\n  2. 예제 관계행렬 선택\n  3. 무작위 관계행렬 생성\n  0. 종료")
        menu = input("  메뉴 선택 > ").strip()
        if menu == "1":
            M = input_matrix()
        elif menu == "2":
            M = choose_example()
        elif menu == "3":
            M = random_matrix()
            print("  무작위 관계행렬을 생성했습니다.")
        elif menu == "0":
            print("  프로그램을 종료합니다.")
            break
        else:
            print(red("  [입력 오류] 0 ~ 3 중에서 선택하세요."))
            continue
        next_step("[1] 입력 행렬 확인 · [2] 동치 관계 판별")
        run(M)
        next_step("메뉴로 돌아가기")


if __name__ == "__main__":
    main()
