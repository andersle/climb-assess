import datetime


_DATE_FMT = '%d.%m.%Y %H:%M:%S'


def read_questions(filename):
    """Read questions from the given file."""
    questions = []
    mapping = {}
    with open(filename, 'r') as infile:
        for i, lines in enumerate(infile):
            split = lines.split('|')
            question = split[0].strip()
            category = split[1].strip()
            questions.append((i, question))
            mapping[i] = category
    return questions, mapping


def read_scorings(filename):
    """Read the scorings for the questions from the given file."""
    scorings = {}
    with open(filename, 'r') as infile:
        for i, lines in enumerate(infile):
            split = lines.split('=')
            scorings[split[1].strip()] = int(split[0].strip())
    return scorings


def ask_questions(questions, scorings, mapping):
    """Ask the questions and score each one.

    Parameters
    ----------
    questions : list of strings
        These are the questions we will ask.
    scorings : list of tuples
        The scorings contain the numerical score and the text
        representation of the possible answers.
    mapping : dict
        A mapping from questions to categories.

    Returns
    -------
    out[0] : dict
        The score for each question.
    out[1] : dict
        The score for each category
    out[2] : object like :py:class:`datetime.datetime`
        A time stamp for starting the questions.
    """
    now = datetime.datetime.now()
    result_q = {}
    result_c = {}
    for idx, question in questions:
        answer = 0
        result_q[idx] = answer
        category = mapping[idx]
        if not category in result_c:
            result_c[category] = 0
        result_c[category] += answer
        print(idx, question, category)
    return result_q, result_c, now


def store_results(outfile, result_q, time):
    """Store results from a set of questions to a file.

    Parameters
    ----------
    outfile : string
        The file we will store to, if this file already exists, the
        results will be appended.
    result_q : dict
        The score for each question.
    time : object like :py:class:`datetime.datetime`
        A time stamp for starting the questions.
    """
    with open(outfile, 'a') as output:
        out = ['time:', '"{}"'.format(time.strftime(_DATE_FMT)), 'answers:']
        for key in sorted(result_q.keys()):
            out.append('{}={}'.format(key, result_q[key]))
        out.append('\n')
        output.write(' '.join(out))



def main():
    questions, mapping = read_questions('questions.txt')
    scorings = read_scorings('scoring.txt')
    result_q, result_c, time = ask_questions(questions, scorings, mapping)
    store_results('results.txt', result_q, time)
    print(result_c)


if __name__ == '__main__':
    main()
