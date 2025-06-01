program InvalidParamType;

function add(a, b: Integer): Integer;
begin
  add := a + b;
end;

var
  result: Integer;
begin
  result := add(5, 'hello');  // Semantic error: passing string instead of integer
end.