__all__ = ['KELVIN', 'CrankNicolsonSolver', 'four_minutes_a_side', 'every_15_secs',
           'sear_then_cook_low', 'sous_vide_liquid_nitrogen', 'slow_roast',
          'hv', 'np', 'cook_recipe', 'snapshots_to_protein_state', 'PROTEIN_STATES']

import holoviews as hv
hv.extension('bokeh', logo=False)



import numpy as np
from enum import Enum

KELVIN  = 273.15   

class BC(Enum):
    """A class for holding boundary conditions."""
    HEATING_LEFT = 0
    HEATING_RIGHT = 1
    HEATING_BOTH = 2
    NO_HEATING = 3

def assemble_A_matrix(N, D, dx, dt, boundary_condition):
    sigma = D * dt / (2 * dx**2)
    A = np.zeros((N+1, N+1))
    for i in range(N+1):
        if i == 0:
            # imposed temperature
            if boundary_condition == BC.HEATING_LEFT or boundary_condition == BC.HEATING_BOTH:
                A[i, i] =  1
            # zero heat flux    
            elif boundary_condition == BC.HEATING_RIGHT or boundary_condition == BC.NO_HEATING:
                A[i, 0] = 1 + sigma
                A[i, 1] = - sigma
        elif i==N:
            # imposed temperature
            if boundary_condition == BC.HEATING_RIGHT or boundary_condition == BC.HEATING_BOTH:
                A[i, i] = 1
            # zero heat flux
            elif boundary_condition == BC.HEATING_LEFT or boundary_condition == BC.NO_HEATING:
                A[i, i-1] = - sigma
                A[i,   i] = 1 + sigma
        else:
            A[i, i-1] =       - sigma
            A[i,   i] = 1 + 2 * sigma
            A[i, i+1] =       - sigma
    return A

def assemble_B_matrix(N, D, dx, dt, boundary_condition):
    sigma = D * dt / (2 * dx**2)
    B = np.zeros((N+1, N+1))
    for i in range(N+1):
        if i == 0:
            # imposed temperature
            if boundary_condition == BC.HEATING_LEFT or boundary_condition == BC.HEATING_BOTH:
                B[i, 0] =   0
            # zero heat flux    
            elif boundary_condition == BC.HEATING_RIGHT or boundary_condition == BC.NO_HEATING:
                B[i, 0] = 1 - sigma
                B[i, 1] =     sigma
        elif i==N:
            # imposed temperature
            if boundary_condition == BC.HEATING_RIGHT or boundary_condition == BC.HEATING_BOTH:
                B[i, i] = 0
            # zero heat flux
            elif boundary_condition == BC.HEATING_LEFT or boundary_condition == BC.NO_HEATING:
                B[i, i-1] =     sigma
                B[i,   i] = 1 - sigma
        else:
            B[i, i-1] =         sigma
            B[i,   i] = 1 - 2 * sigma
            B[i, i+1] =         sigma
    return B

def assemble_C_matrix(N, D, dx, dt, boundary_condition, Tl, Tr):
    sigma = D * dt / (2 * dx**2)
    C = np.zeros((N+1,))
    if boundary_condition == BC.HEATING_LEFT or boundary_condition == BC.HEATING_BOTH:
        C[0] = Tl
    if boundary_condition == BC.HEATING_RIGHT or boundary_condition == BC.HEATING_BOTH:
        C[N] = Tr
    return C

def bc_type_checker(Tl, Tr, Tair):
    EPS = 0.001
    if abs(Tl - Tair) < EPS and abs(Tr - Tair) < EPS:
        return BC.NO_HEATING
    elif abs(Tl - Tair) < EPS:
        return BC.HEATING_RIGHT
    elif abs(Tr - Tair) < EPS:
        return BC.HEATING_LEFT
    else:
        return BC.HEATING_BOTH

class CrankNicolsonSolver:
    def __init__(self, x, T_initial, dt, D, verbose=False):
        self.t = 0
        self.dt = dt
        self.x = np.asarray(x).copy()
        self.T = np.asarray(T_initial).copy()
        self.N = self.x.size - 1
        self.dx = self.x[1] - self.x[0]
        self.bc_is_set = False
        self.D = D
        self.last_bc = None
        self.verbose = verbose
        
    def set_boundary_conditions(self, Tl, Tr, Tair):
        if self.last_bc is not None:
            if self.last_bc == (Tl, Tr, Tair):
                return
        bc = bc_type_checker(Tl, Tr, Tair)
        if self.verbose: print(f'[Set_BC] bc found: {bc}')
        A = assemble_A_matrix(self.N, self.D, self.dx, self.dt, bc)
        self.B = assemble_B_matrix(self.N, self.D, self.dx, self.dt, bc)
        self.C = assemble_C_matrix(self.N, self.D, self.dx, self.dt, bc, Tl, Tr)
        if self.verbose: print(f"[Set_BC] inverting matrix A with conditioning {np.linalg.cond(A)}")
        self.Ainv = np.linalg.inv(A)
        self.bc_is_set = True
        self.last_bc = (Tl, Tr, Tair)
        
    def step(self):
        assert self.bc_is_set
        self.T = np.dot(self.Ainv, np.dot(self.B, self.T) + self.C)
        self.t += self.dt
        
    def n_steps(self, n):
        for i in range(n):
            self.step()

def make_snapshots(solver_params, boundary_conditions, tmax, n_snapshots, M=20):
    time_grid = np.linspace(0, tmax, num=n_snapshots)
    dt = time_grid[1] - time_grid[0]
    params = solver_params.copy()
    params['dt'] = dt / M
    solver = CrankNicolsonSolver(**params)
    solver.set_boundary_conditions(**boundary_conditions)
    snapshots = []
    for _ in range(time_grid.size):
        solver.n_steps(M)
        snapshots.append(solver.T.copy())
    return time_grid, snapshots

import re

four_minutes_a_side = """3cm Steak starts at 23°C
150°C and 23°C for 4:00
23°C and 150°C for 4:00
23°C and 23°C for 5:00"""

def parse_input(recipe):
    """Parses the Cook my meat text format and returns a dictionary with data properly formatted."""
    header, *lines =  recipe.split('\n')
    thickness_cm, T_initial = list(map(float, re.findall("([\d.]+)cm Steak starts at ([-\d.]+)°[C]", header)[0]))
    T_initial += KELVIN
    steps = []
    for line in lines:
        Tleft, Tright, mins, secs = re.findall("([-\d.]+)°[C] and ([-\d.]+)°[C] for ([\d]+):(\d{2})", line)[0]
        steps.append((float(Tleft) + KELVIN, float(Tright) + KELVIN, 60 * int(mins) + int(secs)))
    parsed_params = dict(thickness_mm=thickness_cm * 10, initial_temperature_C=T_initial, steps=steps)
    return parsed_params

def griddify(parsed_params, fine_time_grid):
    """Transforms the input temperature data to a regular time grid."""
    data = np.array(parsed_params['steps'])
    temps, t = data[:, :2], data[:, 2]
    t = np.cumsum(t)
    index = 0
    boundary_conditions = []
    for tt in fine_time_grid:
        if tt > t[index]:
            index += 1
            if index >= data.shape[0]:
                index -= 1
        boundary_conditions.append(temps[index])
    return boundary_conditions

def cook_recipe(recipe, n_snapshots=100, M=100, nx=100):
    """Takes a Cook my meat recipe as input, simulates it and returns temperature snapshots."""
    parsed_params = parse_input(recipe)
    total_time = sum([step_time for Tl, Tr, step_time in parsed_params['steps']])
    coarse_time_grid = np.linspace(0, total_time, num=n_snapshots)
    coarse_time_grid_indices = np.arange(n_snapshots) * M
    fine_time_grid = np.linspace(0, total_time, num=n_snapshots * M)
    dt = fine_time_grid[1] - fine_time_grid[0]
    boundary_conditions = griddify(parsed_params, fine_time_grid)
    x = np.linspace(0, parsed_params['thickness_mm'], num=nx)
    Tair = parsed_params['initial_temperature_C']
    T = np.ones_like(x) * Tair
    solver = CrankNicolsonSolver(x, T, dt, D=0.14)
    snapshots = []
    for ind, (t, (Tl, Tr)) in enumerate(zip(fine_time_grid, boundary_conditions)):
        solver.set_boundary_conditions(Tl, Tr, Tair)
        solver.step()
        if ind in coarse_time_grid_indices:
            T = solver.T.copy()
            snapshots.append(T)
    return x, coarse_time_grid, snapshots

every_15_secs = """3cm Steak starts at 23°C
150°C and 23°C for 0:15
23°C and 150°C for 0:15
150°C and 23°C for 0:15
23°C and 150°C for 0:15
150°C and 23°C for 0:15
23°C and 150°C for 0:15
150°C and 23°C for 0:15
23°C and 150°C for 0:15
150°C and 23°C for 0:15
23°C and 150°C for 0:15
150°C and 23°C for 0:15
23°C and 150°C for 0:15
150°C and 23°C for 0:15
23°C and 150°C for 0:15
150°C and 23°C for 0:15
23°C and 150°C for 0:15
150°C and 23°C for 0:15
23°C and 150°C for 0:15
150°C and 23°C for 0:15
23°C and 150°C for 0:15
150°C and 23°C for 0:15
23°C and 150°C for 0:15
150°C and 23°C for 0:15
23°C and 150°C for 0:15"""

sear_then_cook_low = """3cm Steak starts at 23°C
230°C and 23°C for 0:15
23°C and 230°C for 0:15
110°C and 110°C for 2:30
23°C and 23°C for 15:00"""

sous_vide_liquid_nitrogen = """3cm Steak starts at 23°C
53°C and 53°C for 60:00
-200°C and -200°C for 0:30
200°C and 200°C for 2:00"""

from matplotlib import colors

bounds = [40, 50, 55, 60, 70, 120, 180]
norm = colors.BoundaryNorm(boundaries=bounds, ncolors=6, clip=False)

PROTEIN_STATES = {-1: 'Raw', 
                  0: 'Rare',
                  1: 'Medium Rare',
                  2: 'Medium',
                  3: 'Well',
                  4: 'Browned',
                  5: 'Charred'}

def snapshots_to_protein_state(snapshots_K):
    snapshots_C = np.array(snapshots_K) - KELVIN
    protein_states = []
    for time_index in range(1, np.array(snapshots_C).shape[0] + 1):
        max_temps = np.max(snapshots_C[:time_index, :], axis=0)
        proteines_state = norm(max_temps)
        protein_states.append(proteines_state)
    return protein_states

slow_roast = """12cm Steak starts at 23°C
200°C and 23°C for 3:00
23°C and 200°C for 3:00
93°C and 93°C for 100:00
23°C and 23°C for 25:00"""
