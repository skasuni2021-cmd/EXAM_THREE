#region imports
import statistics as stats
import random as rnd
from Polymer import macroMolecule, Position
#endregion


#region helper functions
def get_int_input(prompt, default):
    """
    Gets an integer from the user.
    If the user presses Enter, the default value is used.
    ChatGPT helped write this function.
    """
    user_input = input(prompt)

    if user_input.strip() == "":
        return default

    return int(user_input)


def average_position(positions):
    """
    Calculates the average x, y, and z center of mass.
    """
    x_avg = stats.mean([p.x for p in positions])
    y_avg = stats.mean([p.y for p in positions])
    z_avg = stats.mean([p.z for p in positions])

    return Position(x=x_avg, y=y_avg, z=z_avg)


def std_dev(values):
    """
    Calculates sample standard deviation.
    Returns 0 if there is only one molecule.
    """
    if len(values) < 2:
        return 0.0

    return stats.stdev(values)
#endregion


#region main simulation
def run_polymer_simulation(target_N=1000, number_molecules=50):
    """
    Runs freely jointed chain simulation for many polymer molecules.

    The actual degree of polymerization for each molecule is selected
    from a normal distribution with mean N and standard deviation 0.1N.
    """

    centers_of_mass = []
    end_to_end_distances = []
    radii_of_gyration = []
    molecular_weights = []
    actual_N_values = []

    for i in range(number_molecules):
        # Required by problem statement:
        # N is selected from normal distribution with mean=N and std=0.1N.
        actual_N = int(round(rnd.gauss(target_N, 0.1 * target_N)))

        if actual_N < 1:
            actual_N = 1

        polymer = macroMolecule(degreeOfPolymerization=actual_N)
        polymer.freelyJointedChainModel()

        centers_of_mass.append(polymer.centerOfMass)
        end_to_end_distances.append(polymer.endToEndDistance)
        radii_of_gyration.append(polymer.radiusOfGyration)
        molecular_weights.append(polymer.MW)
        actual_N_values.append(actual_N)

    avg_com = average_position(centers_of_mass)

    # Convert from meters to micrometers
    end_to_end_um = [value * 1e6 for value in end_to_end_distances]
    radius_gyration_um = [value * 1e6 for value in radii_of_gyration]

    # Convert from meters to nanometers
    avg_com_nm = Position(
        x=avg_com.x * 1e9,
        y=avg_com.y * 1e9,
        z=avg_com.z * 1e9
    )

    # PDI = Mw / Mn
    Mn = stats.mean(molecular_weights)
    Mw = sum([mw ** 2 for mw in molecular_weights]) / sum(molecular_weights)
    PDI = Mw / Mn

    results = {
        "avg_com_nm": avg_com_nm,
        "end_avg_um": stats.mean(end_to_end_um),
        "end_std_um": std_dev(end_to_end_um),
        "rg_avg_um": stats.mean(radius_gyration_um),
        "rg_std_um": std_dev(radius_gyration_um),
        "PDI": PDI,
        "actual_N_avg": stats.mean(actual_N_values)
    }

    return results
#endregion


#region output
def print_results(target_N, number_molecules, results):
    """
    Prints polymer statistics in the format requested.
    """

    com = results["avg_com_nm"]

    print(f"Metrics for {number_molecules} molecules of degree of polymerization = {target_N}")
    print(f"Avg. Center of Mass (nm) = {com.x:0.3f}, {com.y:0.3f}, {com.z:0.3f}")

    print("End-to-end distance (μm):")
    print(f"   Average = {results['end_avg_um']:0.3f}")
    print(f"   Std. Dev. = {results['end_std_um']:0.3f}")

    print("Radius of gyration (μm):")
    print(f"   Average = {results['rg_avg_um']:0.3f}")
    print(f"   Std. Dev. = {results['rg_std_um']:0.3f}")

    print(f"PDI = {results['PDI']:0.3f}")
#endregion


#region main
def main():
    """
    Main CLI function.
    """

    target_N = get_int_input("degree of polymerization (1000)?: ", 1000)
    number_molecules = get_int_input("How many molecules (50)?: ", 50)

    results = run_polymer_simulation(target_N, number_molecules)
    print_results(target_N, number_molecules, results)


if __name__ == "__main__":
    main()
#endregion