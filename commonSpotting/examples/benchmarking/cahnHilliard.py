#!/usr/bin/env python

## -*-Pyth-*-
 # ########################################################################
 # FiPy - a finite volume PDE solver in Python
 # 
 # FILE: "cahnHilliard.py"
 #
 # Author: Jonathan Guyer <guyer@nist.gov>
 # Author: Daniel Wheeler <daniel.wheeler@nist.gov>
 #   mail: NIST
 #    www: <http://www.ctcms.nist.gov/fipy/>
 #  
 # ========================================================================
 # This document was prepared at the National Institute of Standards and
 # Technology by employees of the Federal Government in the course of their
 # official duties.  Pursuant to title 17 Section 105 of the United States
 # Code this document is not subject to copyright protection and is in the
 # public domain.  cahnHilliard.py is an experimental work.  NIST assumes
 # no responsibility whatsoever for its use by other parties, and makes no
 # guarantees, expressed or implied, about its quality, reliability, or any
 # other characteristic.  We would appreciate acknowledgement if the 
 # document is used.
 # 
 # This document can be redistributed and/or modified freely provided that 
 # any derivative works bear some notice that they are derived from it, and
 # any modified versions bear some notice that they have been modified.
 # ========================================================================
 #  See the file "license.terms" for information on usage and 
 #  redistribution of this file, and for a DISCLAIMER OF ALL WARRANTIES.
 # 
 # ########################################################################
 ##

r"""
This example benchmarks the speed and memory usage of solving the
Cahn-Hilliard equation. Run:
    
    $ python setup.py efficiency_test
"""
__docformat__ = 'restructuredtext'

if __name__ == "__main__":
    
    import time

    from fipy import *
    from fipy.tools.parser import parse

    from benchmarker import Benchmarker
    bench = Benchmarker()

    numberOfElements = parse('--numberOfElements', action = 'store', type = 'int', default = 400)


    bench.start()

    nx = int(sqrt(numberOfElements))
    ny = int(sqrt(numberOfElements))

    steps = 10

    dx = 2.
    dy = 2.

    L = dx * nx

    asq = 1.0
    epsilon = 1
    diffusionCoeff = 1

    mesh = Grid2D(dx, dy, nx, ny)

    bench.stop('mesh')

    bench.start()

    from fipy.tools.numerix import random

    var = CellVariable(name = "phase field",
                       mesh = mesh,
                       value = random.random(nx * ny))

    bench.stop('variables')

    bench.start()

    faceVar = var.getArithmeticFaceValue()
    doubleWellDerivative = asq * ( 1 - 6 * faceVar * (1 - faceVar))

    diffTerm2 = ImplicitDiffusionTerm(coeff = (diffusionCoeff * doubleWellDerivative,))
    diffTerm4 = ImplicitDiffusionTerm(coeff = (diffusionCoeff, -epsilon**2))
    eqch = TransientTerm() - diffTerm2 - diffTerm4

    bench.stop('terms')

    bench.start()

    ##solver = LinearLUSolver(tolerance = 1e-15,steps = 1000)
    solver = LinearPCGSolver(tolerance = 1e-15,steps = 1000)

    bench.stop('solver')

    bench.start()

    BCs = (FixedFlux(mesh.getFacesRight(), 0),
           FixedFlux(mesh.getFacesLeft(), 0),
           NthOrderBoundaryCondition(mesh.getFacesLeft(), 0, 3),
           NthOrderBoundaryCondition(mesh.getFacesRight(), 0, 3),
           NthOrderBoundaryCondition(mesh.getFacesTop(), 0, 3),
           NthOrderBoundaryCondition(mesh.getFacesBottom(), 0, 3))

    bench.stop('BCs')

    dexp=-5

    dt = exp(dexp)
    dt = min(100, dt)
    dexp += 0.01
    var.updateOld()
    eqch.solve(var, boundaryConditions = BCs, solver = solver, dt = dt)

    bench.start()

    for step in range(steps):
        dt = exp(dexp)
        dt = min(100, dt)
        dexp += 0.01
        var.updateOld()
        eqch.solve(var, boundaryConditions = BCs, solver = solver, dt = dt)
                
    bench.stop('solve')

    print bench.report(numberOfElements=numberOfElements, steps=steps)