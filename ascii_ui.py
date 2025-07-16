# color_test.py
from color_board import setup_board, print_board, generate_legal_moves, move_piece, can_promote, promote_pawn

def main():
    board = setup_board()
    selected_square = None

    while True:
        promotion_squares = [sq for sq, p in board.items() if can_promote(p, sq)]
        legal_moves = generate_legal_moves(board, selected_square) if selected_square else None

        print_board(board, legal_moves=legal_moves, promotion_squares=promotion_squares, selected_square=selected_square)

        if not selected_square:
            user_input = input("Select piece (e.g., e2) or 'quit': ").strip().lower()
            if user_input == "quit":
                print("Goodbye!")
                break
            if user_input in board:
                selected_square = user_input
            else:
                print("Invalid square or empty. Try again.")
        else:
            user_input = input(f"Enter your move for {selected_square} or 'cancel': ").strip().lower()
            if user_input == "cancel":
                selected_square = None
                continue
            if user_input in legal_moves:
                # Handle promotion if pawn moves to last rank
                if can_promote(board[selected_square], user_input):
                    print("Pawn promotion! Choose piece: q, r, b, n")
                    while True:
                        choice = input("Promote to (q/r/b/n): ").strip().lower()
                        if choice in ['q','r','b','n']:
                            move_piece(board, selected_square, user_input)
                            promote_pawn(board, user_input, choice)
                            break
                        else:
                            print("Invalid choice, please enter q, r, b, or n.")
                else:
                    move_piece(board, selected_square, user_input)
                selected_square = None
            else:
                print("Invalid move. Try again.")

if __name__ == "__main__":
    main()