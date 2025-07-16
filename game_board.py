# color_board.py
from typing import Dict, List, Optional

RESET = "\033[0m"

# Board base colors
BG_LIGHT = "\033[48;5;230m"  # pale tan (light square)
BG_DARK = "\033[48;5;22m"    # forest green (dark square)

# Highlights
HIGHLIGHT_LIGHT = "\033[48;5;229m"  # light yellow (light square highlight)
HIGHLIGHT_DARK = "\033[48;5;120m"   # light green (dark square highlight)

# Promotion squares highlight (50% purple tint)
PROMO_LIGHT = "\033[48;5;183m"  # light purple (light square promotion)
PROMO_DARK = "\033[48;5;91m"    # darker purple (dark square promotion)

# Selected square highlight (gold)
SELECTED_BG = "\033[48;5;220m"

COLS = "abcdefgh"

def setup_board() -> Dict[str, str]:
    board = {}
    for c in COLS:
        board[c + '2'] = 'wp'
        board[c + '7'] = 'bp'
    board.update({
        'a1': 'wr', 'h1': 'wr',
        'b1': 'wn', 'g1': 'wn',
        'c1': 'wb', 'f1': 'wb',
        'd1': 'wq',
        'e1': 'wk',
        'a8': 'br', 'h8': 'br',
        'b8': 'bn', 'g8': 'bn',
        'c8': 'bb', 'f8': 'bb',
        'd8': 'bq',
        'e8': 'bk',
    })
    return board

def can_promote(piece: str, square: str) -> bool:
    if piece not in ('wp', 'bp'):
        return False
    rank = int(square[1])
    return (piece == 'wp' and rank == 8) or (piece == 'bp' and rank == 1)

def generate_legal_moves(board: Dict[str, str], square: str) -> List[str]:
    piece = board.get(square)
    if not piece:
        return []

    color = piece[0]
    ptype = piece[1]

    def inside_board(c, r):
        return 'a' <= c <= 'h' and 1 <= r <= 8

    moves = []
    col = square[0]
    row = int(square[1])
    enemy_color = 'b' if color == 'w' else 'w'

    directions = []

    if ptype == 'p':
        forward = 1 if color == 'w' else -1
        fwd_sq = col + str(row + forward)
        if inside_board(col, row + forward) and fwd_sq not in board:
            moves.append(fwd_sq)
            start_row = 2 if color == 'w' else 7
            if row == start_row:
                two_fwd = col + str(row + 2 * forward)
                if two_fwd not in board:
                    moves.append(two_fwd)
        for dc in [-1, 1]:
            new_col = chr(ord(col) + dc)
            diag_sq = new_col + str(row + forward)
            if inside_board(new_col, row + forward):
                if diag_sq in board and board[diag_sq].startswith(enemy_color):
                    moves.append(diag_sq)
    elif ptype == 'r':
        directions = [(1,0), (-1,0), (0,1), (0,-1)]
    elif ptype == 'b':
        directions = [(1,1), (1,-1), (-1,1), (-1,-1)]
    elif ptype == 'q':
        directions = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
    elif ptype == 'k':
        for dc in [-1,0,1]:
            for dr in [-1,0,1]:
                if dc == 0 and dr == 0:
                    continue
                new_col = chr(ord(col) + dc)
                new_row = row + dr
                if inside_board(new_col, new_row):
                    target = new_col + str(new_row)
                    if target not in board or board[target][0] != color:
                        moves.append(target)
    elif ptype == 'n':
        knight_moves = [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]
        for dc, dr in knight_moves:
            new_col = chr(ord(col) + dc)
            new_row = row + dr
            if inside_board(new_col, new_row):
                target = new_col + str(new_row)
                if target not in board or board[target][0] != color:
                    moves.append(target)

    if directions:
        for dc, dr in directions:
            step = 1
            while True:
                new_col = chr(ord(col) + dc*step)
                new_row = row + dr*step
                if not inside_board(new_col, new_row):
                    break
                target = new_col + str(new_row)
                if target in board:
                    if board[target][0] != color:
                        moves.append(target)
                    break
                moves.append(target)
                step += 1

    return moves

def promote_pawn(board: Dict[str, str], square: str, new_piece_type: str) -> None:
    color = board[square][0]
    board[square] = color + new_piece_type

def print_board(board: Dict[str, str], legal_moves: Optional[List[str]] = None,
                promotion_squares: Optional[List[str]] = None,
                selected_square: Optional[str] = None) -> None:

    cols = "abcdefgh"
    col_indices = {c:i for i,c in enumerate(cols)}

    print()
    print("       " + "         ".join(cols))
    print("  ⌜" + "─────────┬" * 7 + "─────────⌝")

    for r in reversed("12345678"):
        for line in ["top", "mid", "bot"]:
            if line == "top":
                print(f"{r} │", end="")
            else:
                print("  │", end="")

            for c in cols:
                sq = c + r
                idx_sum = col_indices[c] + int(r)
                if idx_sum % 2 == 0:
                    base_bg = BG_LIGHT
                    highlight_bg = HIGHLIGHT_LIGHT
                    promo_bg = PROMO_LIGHT
                else:
                    base_bg = BG_DARK
                    highlight_bg = HIGHLIGHT_DARK
                    promo_bg = PROMO_DARK

                bg = base_bg

                if promotion_squares and sq in promotion_squares:
                    bg = promo_bg
                elif legal_moves and sq in legal_moves:
                    bg = highlight_bg
                if selected_square == sq:
                    bg = SELECTED_BG

                piece = board.get(sq, "")
                piece_str = piece.center(5) if piece else "     "

                if line == "top" or line == "bot":
                    print(bg + "         " + RESET, end="│")
                elif line == "mid":
                    print(bg + f"  {piece_str}  " + RESET, end="│")

            if line == "mid":
                print()
            else:
                print()

        if r != "1":
            print("  ├" + "─────────┼" * 7 + "─────────┤")

    print("  ⌞" + "─────────┴" * 7 + "─────────⌟")

def move_piece(board: Dict[str, str], start: str, end: str) -> bool:
    legal_moves = generate_legal_moves(board, start)
    if end not in legal_moves:
        return False
    board[end] = board[start]
    del board[start]
    return True