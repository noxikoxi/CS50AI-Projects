import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])
    # print(people)
    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }
    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def pass_parent(number_of_genes, parent_genes):
    """
    Calculate probability of parent passing specific number of genes
    """

    mutation = PROBS["mutation"]

    # parent passes 0 genes
    if parent_genes == 0:
        parent0 = 1 - mutation
    elif parent_genes == 1:
        parent0 = (0.5 * (1 - mutation)) + (0.5 * mutation)
    else:
        parent0 = mutation

    # parent passed 1 gene
    if parent_genes == 0:
        parent1 = mutation
    elif parent_genes == 1:
        parent1 = (0.5 * (1 - mutation)) + (0.5 * mutation)
    else:
        parent1 = 1 - mutation

    if number_of_genes == 0:
        return parent0
    elif number_of_genes == 1:
        return parent1


def calc_parents(number_of_genes, father_gene, mother_gene):
    """
    Calculate the probability of having number of genes given parents
    """
    if number_of_genes == 0:
        probability = pass_parent(0, father_gene) * pass_parent(0, mother_gene)
    elif number_of_genes == 1:
        probability = (pass_parent(0, father_gene) * pass_parent(1, mother_gene)
                       + pass_parent(0, mother_gene) * pass_parent(1, father_gene))
    else:  # 2 genes
        probability = pass_parent(1, father_gene) * pass_parent(1, mother_gene)

    return probability


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        1 * everyone in set `one_gene` has one copy of the gene, and
        2 * everyone in set `two_genes` has two copies of the gene, and
        3 * everyone not in `one_gene` or `two_gene` does not have the gene, and
        4 * everyone in set `have_trait` has the trait, and
        5 * everyone not in set` have_trait` does not have the trait.
    """
    probability = 1

    for person in people:
        father_gene = 0
        mother_gene = 0

        if people[person]["mother"] is None and people[person]["father"] is None:  # No parents
            parents = False
        else:
            parents = True
            mother = people[person]["mother"]
            father = people[person]["father"]

            # calculating parents genes
            if mother in one_gene:
                mother_gene = 1
            elif mother in two_genes:
                mother_gene = 2
            else:
                mother_gene = 0

            if father in one_gene:
                father_gene = 1
            elif father in two_genes:
                father_gene = 2
            else:
                father_gene = 0

        # Person in set 'one_gene'
        if person in one_gene:
            if parents:
                probability *= calc_parents(1, father_gene, mother_gene)
            else:
                probability *= PROBS["gene"][1]

        # Person in set 'two_genes'
        if person in two_genes:
            if parents:
                probability *= calc_parents(2, father_gene, mother_gene)
            else:
                probability *= PROBS["gene"][2]

        # Person not in 'one_gene' and not in 'two_genes' and doesn't have the gene
        if person not in one_gene and person not in two_genes:
            if parents:
                probability *= calc_parents(0, father_gene, mother_gene)
            else:
                probability *= PROBS["gene"][0]

        # Person in set 'have_trait' and has trait
        if person in have_trait:
            if person in one_gene:
                probability *= PROBS["trait"][1][True]
            elif person in two_genes:
                probability *= PROBS["trait"][2][True]
            else:
                probability *= PROBS["trait"][0][True]

        # Person not in set 'have_trait' and does not have trait
        if person not in have_trait:
            if person in one_gene:
                probability *= PROBS["trait"][1][False]
            elif person in two_genes:
                probability *= PROBS["trait"][2][False]
            else:
                probability *= PROBS["trait"][0][False]

    return probability


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        # normalizing gene chance
        sum_gene = 0
        for value in probabilities[person]["gene"]:
            sum_gene += probabilities[person]["gene"][value]
        if sum_gene != 1:
            for value in probabilities[person]["gene"]:
                probabilities[person]["gene"][value] /= sum_gene

        # normalizing trait chance
        sum_trait = 0
        for value in probabilities[person]["trait"]:
            sum_trait +=  probabilities[person]["trait"][value]
        if sum_trait != 1:
            for value in probabilities[person]["trait"]:
                probabilities[person]["trait"][value] /= sum_trait


if __name__ == "__main__":
    main()
