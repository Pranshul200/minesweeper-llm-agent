def board_string_to_2d_list(board_str: str) -> list[list[str]]:
    """
    Converts a multiline board string to a 2D list of strings.
    Example input:
    0 0 0 1 ?
    0 0 1 2 ?
    0 0 1 * ?
    0 0 1 2 ?
    0 0 0 1 ?
    """
    lines = board_str.strip().split('\n')
    board_2d = [line.strip().split() for line in lines if line.strip()]
    for row in board_2d:
        for col in range(len(row)):
            if row[col] == '?':
                row[col] = 'Hidden'
            elif row[col] == 'F':
                row[col] = 'Flag' 
    return board_2d
def generate_prompt(board: str, history: list[str], rows: int, cols: int, total_mines: int) -> str:
    """
    Generates a strict prompt for the LLM agent to play Minesweeper using logic only.
    """
    history_str = "\n".join(history) if history else "None"
    board_2d = board_string_to_2d_list(board)

    # Render board in readable row-wise format with row numbers
    def render_board_verbal(board_2d: list[list[str]]) -> str:
        lines = {}
        for row_idx, row in enumerate(board_2d):
            words = []
            for cell in row:
                if cell == 'Hidden':
                    words.append("hidden")
                elif cell == 'Flag':
                    words.append("flag")
                else:
                    words.append(str(cell))
            # column_json = {}
            # for col_idx, word in enumerate(words):
            #     column_json[f"Col{col_idx}"] = word        
            lines[f"Row{row_idx+1}"] = words
                 
            # lines.append(f"Row {row_idx}: " + ", ".join(words))
        return lines

    board_text = render_board_verbal(board_2d)

    return f"""

You are playing a game called Minesweeper on a board with {rows} rows and {cols} columns. 
Your objective is to reveal a safe cell. If you reveal a mine, you lose. If you reveal a safe cell, you win.

Input board:
```
{board}
```


**Board Format**:
- Used \n to separate rows.
- Used space to separate columns in a single row.
- A number (number of adjacent mines) to that cell i.e horizontal, vertical, and diagonal neibhors
- '?' for hidden cells
    example board:
    ```
    0 ? ?
    ? 1 1
    ? ? ?
    ```
    The above example board has 3 rows and 3 columns:
    (row1,col1) = 0, (row1,col2) = ?, (row1,col3) = ?
    (row2,col1) = ?, (row2,col2) = 1, (row2,col3) = 1
    (row3,col1) = ?, (row3,col2) = ?, (row3,col3) = ?
    This means revealed cells are -> (row1,col1) = 0, (row2,col2) = 1, (row2,col3) = 1
    Hidden cells are -> (row1,col2) = ?, (row2,col1) = ?, (row3,col1) = ?, (row3,col2) = ?, (row3,col3) = ?

**NOTE-ENSURE TO REVEAL ONLY THE CELLS WHICH ARE PRESENT AS `?` that means are Hidden in the board. 
    

**Important Instructions**: 
- Row numbers go from 1 to {rows}.
- Column numbers go from 1 to {cols}.
- Assume one based indexing for rows and columns.
- NEVER select a cell outside this board.
- If all the cells are hidden, you can reveal any random cell assuming that it is a safe cell.
- Only one move is allowed per turn.
- `0` means no adjacent mines, `1` means one adjacent mine, and so on up to `8`.

NOTE: All revealed cells are marked as `0-8`, So do not reveal a cell which is already a number betweeen `0-8`.Only reveal cells which having `hidden` value

Use the below example for better understnading of the game:

Example 1:
    Example Input board:
    ```
    ? ? ? ? ? ?
    1 2 2 2 ? ?
    0 0 0 1 1 1
    0 0 0 0 0 0
    0 0 0 0 0 0
    0 0 0 0 0 0
    ```
    

    Output:
    
    {{"action": "reveal", "row": 2, "col": 6}}
    

    
***Very Important Instruction***:

YOU CAN REVEAL ONLY ONE CELL AT A TIME.
Do not choose a cell outside the board (row 1–{rows}, col 1–{cols}).

OUTPUT FORMAT (very strict)
Return **only** a JSON object with three keys in below format:

{{"action": "reveal", "row": <int>, "col": <int>}} 

- MAKE SURE TO NOT GIVE EXPLAINATION OR ANY OTHER TEXT, JUST THE JSON OBJECT.


"""