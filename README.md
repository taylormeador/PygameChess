# PygameChess

I am creating Chess in Pygame by following this tutorial series: https://www.youtube.com/watch?v=EnYui0e73Rs.
My plan is to add my own features and generate as much of the code as possible on my own; however, this is primarily a learning experience for me to get more comfortable with OOP principles, and completing larger projects.

-8/24/21
The  game is partially playable in its current state. All the pieces can move and make captures, but there is no logic for check/checkmate so you can't win the game and also the king can make moves that are illegal. Some other moves have not been implemented yet such as en passant and pawn promotion.

-9/22/21
Added pawn promotion (auto-queen only) and en passant captures. I hope to add logic for castling next

-10/4/21
Added castling

-10/6/21
Added an AI that plays random moves. Letting it play itself also revealed several bugs that were fixed

-10/7/21
Improved AI to use a recursive MinMax algorithm to find better moves. Added a feature that highlights the square of the piece that last moved