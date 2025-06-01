program SomaArray;

var
  numeros: array[1..5] of integer;
  i, soma: integer;

begin
  soma := 0;
  writeln('Introduza 5 números inteiros:');

  for i := 5 downto 1 do
  begin
    readln(numeros[i]);
    soma := soma + numeros[i];
  end;

  writeln('A soma dos números é: ', soma);
end.