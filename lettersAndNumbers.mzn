% MIT License

% Copyright (c) 2022 Kelvin Davis

% Permission is hereby granted, free of charge, to any person obtaining a copy
% of this software and associated documentation files (the "Software"), to deal
% in the Software without restriction, including without limitation the rights
% to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
% copies of the Software, and to permit persons to whom the Software is
% furnished to do so, subject to the following conditions:

% The above copyright notice and this permission notice shall be included in all
% copies or substantial portions of the Software.

% THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
% IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
% FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
% AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
% LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
% OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
% SOFTWARE.

include "globals.mzn";

int: n;
set of int: N = 1..n;
set of int: M = 1..(2*n-1);
array[N] of int: numbers;
int: target;

% Binary Tree
set of int: N_opt = {0} union N; % These sets are for values in
set of int: M_opt = {0} union M; % the arrays
enum Tokens = {Val, Add, Sub, Mul, Div, Null};

array[M] of var Tokens: tree;
array[M] of var M_opt: left;
array[M] of var M_opt: right;
array[M] of var M_opt: lowest;
array[M] of var M_opt: highest;

array[M] of var N_opt: indexes;
constraint count(indexes, 0, n-1);
constraint alldifferent_except_0(indexes);

% tree (array) has n leaves
constraint count(tree, Val, n);

% separate tree from unused items
var M: tree_depth = highest[1];
var N: used;
constraint 2*used-1 = tree_depth;

% Constrain leaves and nodes
constraint forall (i in 1..tree_depth) (
  is_leaf(i) \/ is_node(i)
);
% Constrain unused items
constraint forall (i in M where i > tree_depth) (
  is_unused(i)
);

% Leaves have no children are the highest and lowest nodes in their subtree
predicate is_leaf(var M: i) = (
  tree[i] = Val /\
  left[i] == 0 /\
  right[i] == 0 /\
  highest[i] == i /\
  lowest[i] == i /\
  indexes[i] != 0 /\
  true
);

% node constraint
predicate is_node(var M: i) = (
  tree[i] != Val /\ tree[i] != Null /\
  tree[left[i]] != Null /\ tree[right[i]] != Null /\
  left[i] > i /\
  left[i] = i + 1 /\
  right[i] > i /\
  right[i] > left[i] /\
  right[i] > highest[left[i]] /\
  right[i] = highest[left[i]] + 1 /\
  lowest[i] = i /\
  highest[i] = highest[right[i]] /\
  indexes[i] = 0 /\
  true
);

% unused constraint
predicate is_unused(var M: i) = (
  (tree[i] = Null \/ tree[i] = Val) /\
  left[i] = 0 /\
  right[i] = 0 /\
  (tree[i] = Val -> indexes[i] != 0) /\
  (tree[i] = Null -> indexes[i] = 0) /\
  lowest[i] = 0 /\
  highest[i] = 0 /\
  true
);

% Tree subtree values
array[M] of var -10000..10000: tree_vals;
constraint forall (i in M) (
  (tree[i] == Val -> tree_vals[i] = numbers[indexes[i]]) /\
  (tree[i] == Add -> tree_vals[i] = tree_vals[left[i]] + tree_vals[right[i]]) /\
  (tree[i] == Sub -> tree_vals[i] = tree_vals[left[i]] - tree_vals[right[i]]) /\
  (tree[i] == Mul -> tree_vals[i] = tree_vals[left[i]] * tree_vals[right[i]]) /\
  (tree[i] == Div -> (
    tree_vals[i] = tree_vals[left[i]] div tree_vals[right[i]] /\
    tree_vals[left[i]] mod tree_vals[right[i]] == 0
  )) /\
  (tree[i] == Null -> tree_vals[i] = 0)
);

/*constraint tree_vals[1] = target;*/

solve :: int_search([used], input_order, indomain_min)
  minimize 10*abs(tree_vals[1] - target) + used;
