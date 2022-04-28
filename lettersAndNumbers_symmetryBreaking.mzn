%/**
% * Break Symmetry
% */

% no sub-expression can be negative
% constraint symmetry_breaking_constraint(
%   forall (i in M) (
%     tree_vals[i] >= 0
%   )
% );

% string of additions and subtractions must be associative in one direction
% the values of the string must be in sorted order

% Associativity of Addition: (a+b)+c = a+(b+c)
constraint symmetry_breaking_constraint(
  forall (i in M) (
    tree[i] = Add -> tree[left[i]] != Add
  )
);
% Identity of Addition: a = 0+a = a+0
constraint symmetry_breaking_constraint(
  forall (i in M) (
    tree[i] = Add -> (tree_vals[left[i]] != 0 /\ tree_vals[right[i]] != 0)
  )
);
% Associativity of Multiplication: (a*b)*c = a*(b*c)
constraint symmetry_breaking_constraint(
  forall (i in M) (
    tree[i] = Mul -> tree[left[i]] != Mul
  )
);
% Identity of Multiplication: a = 1*a = a*1
constraint symmetry_breaking_constraint(
  forall (i in M) (
    tree[i] = Mul -> (tree_vals[left[i]] != 1 /\ tree_vals[right[i]] != 1)
  )
);
% Symmetry of Addition and Multiplication: a+b = b+a and a*b = b*a
constraint symmetry_breaking_constraint(
  forall (i in M) (
    (tree[i] == Add \/ tree[i] == Mul) -> tree[left[i]] <= tree[right[i]]
  )
);
% (a-b)-c = a-(b+c)
constraint symmetry_breaking_constraint(
  forall (i in M) (
    tree[i] = Sub -> tree[left[i]] != Sub
  )
);

% Distributivity of Multiplication
% a*(b+c) = a*b + a*c
%         = b*a + a*c
%         = a*b + c*a
%         = b*a + c*a
% a*(b-c) = a*b - a*c
%         = b*a - a*c
%         = a*b - c*a
%         = b*a - c*a
constraint symmetry_breaking_constraint(
  forall (i in M) ((
    (tree[i] = Add \/ tree[i] = Sub) /\
    tree[left[i]] = Mul /\ tree[right[i]] = Mul) -> (
      tree_vals[left[left[i]]] != tree_vals[left[right[i]]] /\
      tree_vals[left[left[i]]] != tree_vals[right[right[i]]] /\
      tree_vals[right[left[i]]] != tree_vals[left[right[i]]] /\
      tree_vals[right[left[i]]] != tree_vals[right[right[i]]] /\
      true
    )
  )
);
% Distributivity of Division
% (a+b)/c = a/c + b/c
% (a-b)/c = a/c - b/c
constraint symmetry_breaking_constraint(
  forall (i in M) ((
    (tree[i] = Add \/ tree[i] = Sub) /\
    tree[left[i]] = Div /\ tree[right[i]] = Div) -> (
      tree_vals[right[left[i]]] != tree_vals[right[right[i]]] /\
      true
    )
  )
);
% TODO: check to see if the following two constraints are implied by the Symmetry constraints
constraint symmetry_breaking_constraint(
  forall (i in M) (
    (tree[i] = Add /\ tree[right[i]] = Val) -> tree[left[i]] = Val
  )
);
constraint symmetry_breaking_constraint(
  forall (i in M) (
    (tree[i] = Mul /\ tree[right[i]] = Val) -> tree[left[i]] = Val
  )
);
constraint symmetry_breaking_constraint(
  forall (i in M) (
    (tree[i] = Add /\ tree[left[i]] = Val /\ tree[right[i]] = Val) ->
      indexes[left[i]] < indexes[right[i]]
  )
);
constraint symmetry_breaking_constraint(
  forall (i in M) (
    (tree[i] = Mul /\ tree[left[i]] = Val /\ tree[right[i]] = Val) ->
      indexes[left[i]] < indexes[right[i]]
  )
);
constraint symmetry_breaking_constraint(
  forall (i in M) (
    (tree[i] = Add /\ tree[left[i]] = Val /\ tree[right[i]] = Add /\
      tree[left[right[i]]] = Val) ->
      indexes[left[i]] < indexes[left[right[i]]]
  )
);
constraint symmetry_breaking_constraint(
  forall (i in M) (
    (tree[i] = Mul /\ tree[left[i]] = Val /\ tree[right[i]] = Mul /\
      tree[left[right[i]]] = Val) ->
      indexes[left[i]] < indexes[left[right[i]]]
  )
);

% all numbers with the same value should be assigned in sorted order
constraint symmetry_breaking_constraint(
  forall (i in M) (
    forall (j in M where i < j) (
      (
        tree[i] = Val /\
        tree[j] = Val /\
        numbers[indexes[i]] = numbers[indexes[j]]
      ) -> indexes[i] < indexes[j]
    )
  )
);

% Sort the nodes of equivalent value
% This one might be invalid as 1 * 100 has 100 as a leaf
% TODO: This might not be good <don't know the word here>
% TODO: write a logical proof as to why this works or doesn't work
constraint symmetry_breaking_constraint(
  forall (i in M) (
    forall (j in M where i < j) (
      (
        tree_vals[i] = tree_vals[j]
      ) -> tree[i] >= tree[j]
    )
  )
);

