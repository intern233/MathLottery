import SunBeta
open scoped BigOperators

#check @SunBeta.beta_coeffwise_logconvex
#print SunBeta.beta
#print axioms SunBeta.beta_coeffwise_logconvex

-- A separate statement written directly from the original problem.
example (n : ℕ) (hn : 1 ≤ n) (d : ℕ) :
    0 ≤ ((∑ k ∈ Finset.range ((n-1)+1),
      Polynomial.monomial k (((n-1).choose k : ℤ)^2 * (((n-1)+k).choose k : ℤ))) *
      (∑ k ∈ Finset.range ((n+1)+1),
      Polynomial.monomial k (((n+1).choose k : ℤ)^2 * (((n+1)+k).choose k : ℤ))) -
      (∑ k ∈ Finset.range (n+1),
      Polynomial.monomial k ((n.choose k : ℤ)^2 * ((n+k).choose k : ℤ)))^2
      : Polynomial ℤ).coeff d := by
  exact SunBeta.beta_coeffwise_logconvex n hn d
