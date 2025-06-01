program CallSquareDemo;

{ Declaração da função que calcula o quadrado de um inteiro }
function Square(n: Integer): Integer;
begin
  Square := n * n;
end;

var
  num: Integer;
  r: Integer;

begin
  num := 3;

  { Chamada da função square e armazenamento do resultado }
  r := Square(num);
end.
