import numpy as np
from numpy.core.multiarray import concatenate
import pandas as pd
import wrapr as wr


SSBtools = wr.library("SSBtools")
GaussSuppression = wr.library("GaussSuppression")

num = np.array([100, 90, 10, 80, 20, 70, 30, 80, 10, 10,
                70, 10, 10, 10, 60, 20, 10, 10])
v1 = np.concatenate((np.array("v1")[np.newaxis], 
                     np.repeat(["v2", "v3", "v4"], 2),
                     np.repeat("v5", 3), 
                     np.repeat(["v6", "v7"], 4)))
sw2 = np.array([1, 2, 1, 2, 1, 2, 1, 2, 1, 1, 2, 
                 1, 1, 1, 2, 1, 1, 1])
sw3 = np.array([1, 0.9, 1, 2, 1, 2, 1, 2, 1, 1, 
                 2, 1, 1, 1, 2, 1, 1, 1])

d = pd.DataFrame({
    "v1"  : v1,
    "num" : num,
    "sw1" : 1,
    "sw2" : sw2,
    "sw3" : sw3
    }
  )

mm = SSBtools.ModelMatrix(d, formula = "~ v1 - 1", 
                          crossTable = True)
p1 = GaussSuppression.DominanceRule(
      d,
      x = mm["modelMatrix"],
      crossTable = mm["crossTable"],
      numVar = "num",
      n = 2,
      k = 90
    )

p2 = GaussSuppression.DominanceRule(
        d,
        x = mm["modelMatrix"],
        crossTable = mm["crossTable"],
        numVar = "num",
        n = 2,
        k = 90,
        sWeightVar = "sw1",
        domWeightMethod = "tauargus"
        )
  p3 =
    DominanceRule(
      d,
      x = mm$modelMatrix,
      crossTable = mm$crossTable,
      numVar = "num",
      n = 2,
      k = 90,
      sWeightVar = "sw1",
    )
  expect_true(all.equal(as.logical(p1), p2$primary, p3$primary))
})

test_that("Default weighted dominance", {
  p =
    DominanceRule(
      d,
      x = mm$modelMatrix,
      crossTable = mm$crossTable,
      numVar = "num",
      n = 2,
      k = 90,
      sWeightVar = "sw2",
    )
  expect_equal(p$primary, c(T, rep(F, 6)))
})

test_that("tauargus dominance", {
  p =
    DominanceRule(
      d,
      x = mm$modelMatrix,
      crossTable = mm$crossTable,
      numVar = "num",
      n = 2,
      k = 90,
      sWeightVar = "sw2",
      domWeightMethod = "tauargus"
    )
  expect_equal(p$primary, c(T, T, F, F, F, F, F))
  expect_warning(
    DominanceRule(
      d,
      x = mm$modelMatrix,
      crossTable = mm$crossTable,
      numVar = "num",
      n = 2,
      k = 90,
      sWeightVar = "sw3",
      domWeightMethod = "tauargus"
    )
  )
  expect_error(
    DominanceRule(
      d,
      x = mm$modelMatrix,
      crossTable = mm$crossTable,
      numVar = "num",
      n = 2,
      k = 90,
      charVar = "v1",
      sWeightVar = "sw1",
      domWeightMethod = "tauargus"
    )
  )
})
