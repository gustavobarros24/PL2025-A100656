program TwoFuncs;

function Add(a, b: Integer): Integer;
begin
  Add := a + b;
end;

function Multiply(a, b: Integer): Integer;
begin
  Multiply := a * b;
end;

var
  x, y: Integer;
begin
  x := 3;
  y := 4;
  WriteLn('Add: ', Add(x, y));
  WriteLn('Multiply: ', Multiply(x, y));
end.