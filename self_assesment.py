import datetime
import random
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec


_DATE_FMT = '%d.%m.%Y-%H:%M:%S:%f'
_DATE_FMT_PNG = '%d.%m.%Y.%H.%M.%S.%f'


COLORS = {
    'mental': '#4C72B0',
    'technique': '#55A868',
    'physical': '#C44E52',
}


CATEGORIES = {
    'mental': 'Mental',
    'technique': 'Technique and Tactics',
    'physical': 'Physical',
}


def read_questions(filename):
    """Read questions from the given file.

    Parameters
    ----------
    filename : string
        The file to read questions from.

    Returns
    -------
    out[0] : dict of strings
        The questions. The keys are the ids of the question.
    out[1] : dict of strings
        A mapping for each question to a category.
    """
    questions = {}
    mapping = {}
    with open(filename, 'r') as infile:
        for i, lines in enumerate(infile):
            split = lines.split('|')
            question = split[0].strip()
            category = split[1].strip()
            questions[i] = question
            mapping[i] = category
    return questions, mapping


def read_scorings(filename):
    """Read the scorings for the questions from the given file.

    Parameters
    ----------
    filename : string
        The file to read questions from.

    Returns
    -------
    out : dict of ints
        The score for the possible answers. The keys for this dict
        are the possible answers and the corresponding integer the
        score.
    """
    scorings = {}
    with open(filename, 'r') as infile:
        for lines in infile:
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
    for idx in sorted(questions.keys()):
        question = questions[idx]
        answer = random.randint(0, 5)
        result_q[idx] = answer
        category = mapping[idx]
        if category not in result_c:
            result_c[category] = 0
        result_c[category] += answer
        print(idx, question, category, scorings)
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
        out = ['time={}'.format(time.strftime(_DATE_FMT))]
        for key in sorted(result_q.keys()):
            out.append('{}={}'.format(key, result_q[key]))
        out.append('\n')
        output.write(' '.join(out))


def read_results(filename, mapping):
    """Read results from the given file.

    Parameters
    ----------
    filename : string
        The file to read from.
    mapping : dict
        A mapping from questions to categories.

    Returns
    -------
    out : list of dicts
        Each item in this list correspond to scores for a set of
        questions. The dics also contain the time stamp as an
        object like :py:class:`datetime.datetime`.
    """
    results = []
    with open(filename, 'r') as infile:
        for lines in infile:
            split = lines.strip().split()
            new_result = {'time': None, 'result_q': {}, 'result_c': {}}
            for i in split:
                spliti = i.split('=')
                if spliti[0] == 'time':
                    time = datetime.datetime.strptime(spliti[1], _DATE_FMT)
                    new_result['time'] = time
                else:
                    idx = int(spliti[0])
                    answer = int(spliti[1])
                    new_result['result_q'][idx] = answer
                    category = mapping[idx]
                    if category not in new_result['result_c']:
                        new_result['result_c'][category] = 0
                    new_result['result_c'][category] += answer
            results.append(new_result)
    return results


def plot_score_questions(results):
    """Plot scores for all questions as function of time."""
    fig = plt.figure(figsize=(12, 8))
    nrow, ncol = 10, 3
    grid = gridspec.GridSpec(nrow, ncol)
    axes = []
    for i in range(nrow * ncol):
        row = i // ncol
        col = i % ncol
        axi = fig.add_subplot(grid[row, col])
        axes.append(axi)
    # collect the data on form (time1, time2, ...) (answer11, answer12, ...)
    dates = [result['time'] for result in results]
    answers = {}
    for result in results:
        for idx, answer in result['result_q'].items():
            if idx not in answers:
                answers[idx] = []
            answers[idx].append(answer)
    for idx, answer in answers.items():
        axi = axes[idx]
        axi.plot_date(dates, answer, xdate=True, fmt='o-')
    axes[0].set_title('Mental')
    axes[1].set_title('Technique and Tactics')
    axes[2].set_title('Physical')
    for i, axi in enumerate(axes):
        axi.set_ylim(-1, 6)
        row = i // ncol
        col = i % ncol
        if col != 0:
            axi.yaxis.set_ticklabels([])
        if row == nrow - 1:
            pass
        else:
            axi.xaxis.set_ticklabels([])
    fig.tight_layout()
    fig.savefig('all-questions.png')


def plot_results_questions(results, mapping):
    """Plot individual results."""
    for result in results:
        time = result['time']
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(111)
        ax1.set_title(
            'Results for questions on {}'.format(time.strftime(_DATE_FMT))
        )
        handles = []
        labels = []
        for idx, answer in result['result_q'].items():
            category = mapping[idx]
            bari = ax1.bar(idx, answer, width=1, align='center',
                           color=COLORS[category])
            if category not in labels:
                handles.append(bari)
                labels.append(category)
        ax1.axhline(y=3, ls=':', lw=2, alpha=0.6, color='#262626')
        ax1.set_ylim(0, 6)
        ax1.legend(handles, labels)
        fig1.tight_layout()
        fig1.savefig(
            'results-q-{}.png'.format(time.strftime(_DATE_FMT_PNG))
        )


def plot_results_categories(results, mapping):
    """Plot over-all results for categories."""
    for result in results:
        time = result['time']
        results_c = {}
        for idx, answer in result['result_q'].items():
            category = mapping[idx]
            if category not in results_c:
                results_c[category] = 0
            results_c[category] += answer
        fig2 = plt.figure()
        ax2 = fig2.add_subplot(111)
        ax2.set_title(
            'Results for categories on {}'.format(time.strftime(_DATE_FMT))
        )
        for i, key in enumerate(sorted(results_c.keys())):
            ax2.bar(i, results_c[key], width=1, align='center',
                    color=COLORS[key], label=key)
        ax2.legend()
        ax2.set_ylim(0, 60)
        fig2.tight_layout()
        fig2.savefig(
            'results-c-{}.png'.format(time.strftime(_DATE_FMT_PNG))
        )


def table_results_low_questions(results, questions, mapping):
    """Show low-scoring questions."""
    for result in results:
        time = result['time']
        print()
        print(
            'Results for questions on {}'.format(time.strftime(_DATE_FMT))
        )
        low = {}
        for idx, answer in result['result_q'].items():
            category = mapping[idx]
            if answer <= 3:
                if category not in low:
                    low[category] = []
                low[category].append((str(idx), questions[idx], str(answer)))
        for i in sorted(low.keys()):
            title = 'Lowest scoring in category "{}"'.format(CATEGORIES[i])
            table = generate_rst_table(
                low[i], title, ['ID', 'Question', 'Answer']
            )
            for row in table:
                print(row)


def table_results_all_questions(results, questions, mapping):
    """Show answers to all questions."""
    for result in results:
        time = result['time']
        print()
        print(
            'Results for questions on {}'.format(time.strftime(_DATE_FMT))
        )
        answers = []
        categories = {}
        for idx in sorted(result['result_q']):
            answer = result['result_q'][idx]
            category = mapping[idx]
            if category not in categories:
                categories[category] = []
            ans = str(answer)
            if answer <= 3:
                ans += '*'
            categories[category].append((str(idx), questions[idx], ans))
            answers.append((str(idx), questions[idx], ans))
        title = 'Answers for questions'
        table = generate_rst_table(
            answers, title, ['ID', 'Question', 'Answer']
        )
        for row in table:
            print(row)
        for i in sorted(categories):
            title = 'Answers for category "{}"'.format(CATEGORIES[i])
            table = generate_rst_table(
                categories[i], title, ['ID', 'Question', 'Answer']
            )
            for row in table:
                print(row)


def generate_rst_table(table, title, headings):
    """Generate reStructuredText for a table.

    This is a general function to generate a table in reStructuredText.
    The table is specified with a title, headings for the columns and
    the contents of the columns and rows.

    Parameters
    ----------
    table : list of lists
        `table[i][j]` is the contents of column `j` of row `i` of the
        table.
    title : string
        The header/title for the table.
    headings : list of strings
        These are the headings for each table column.
    """
    # for each column, we need to figure out how wide it should be
    # 1) Check headings
    col_len = [len(col) + 2 for col in headings]
    # 2) Check if some of the columns are wider
    for row in table:
        for i, col in enumerate(row):
            if len(col) >= col_len[i] - 2:
                col_len[i] = len(col) + 2  # add some extra space

    width = len(col_len) + sum(col_len) - 1
    topline = '+' + width * '-' + '+'
    # create the header
    str_header = '|{{0:<{0}s}}|'.format(width)
    str_header = str_header.format(title)
    # make format for header:
    head_fmt = ['{{0:^{0}s}}'.format(col) for col in col_len]
    # create first row, which is the header on columns:
    row_line = [fmt.format(col) for fmt, col in zip(head_fmt, headings)]
    row_line = [''] + row_line + ['']
    row_line = '|'.join(row_line)
    # also set-up the horizontal line:
    hline = [''] + [col * '-' for col in col_len] + ['']
    hline = '+'.join(hline)
    # generate table
    str_table = [topline, str_header, hline, row_line, hline.replace('-', '=')]
    for row in table:
        row_line = [fmt.format(col) for fmt, col in zip(head_fmt, row)]
        row_line = [''] + row_line + ['']
        row_line = '|'.join(row_line)
        str_table.extend([row_line, hline])
    return str_table


def main():
    """Run the application."""
    questions, mapping = read_questions('questions.txt')
    # scorings = read_scorings('scoring.txt')
    # result_q, result_c, time = ask_questions(questions, scorings, mapping)
    # store_results('results.txt', result_q, time)
    results = read_results('results.txt', mapping)
    plot_score_questions(results)
    plot_results_questions(results, mapping)
    plot_results_categories(results, mapping)
    table_results_low_questions(results, questions, mapping)
    table_results_all_questions(results, questions, mapping)


if __name__ == '__main__':
    main()
