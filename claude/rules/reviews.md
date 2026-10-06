# Reviews

When the user has to review something - snapshot or output diffs, a spec,
measurement results, generated data, a decision - hand it to them as a review
document, not as commands to run or raw diffs to read in the terminal.

## The review document

Write it as a file in the repo (for example next to the task list that asks
for the review), so it stays as the record. In this order:

1. **What is being reviewed and how**: one paragraph - what changed, why, and
   what the user does with each item.
2. **Automatic checks**: every check a script can make, run before the user
   sees anything, each shown as pass or fail with the offending items.
3. **The items**: each change with a short commentary on its cause. Changes
   with no explanation go in their own list, marked as needing attention.
4. **Decisions**: each decision needed, with concrete options and a
   recommendation where there is one.
5. **Answers**: left empty for the user's verdict, filled in afterwards with
   the date.

Raw diffs are for seeing a change in context, not the way in.

## Make it interactive

Where possible, also publish the review as an interactive web page (an
Artifact) on which the user approves or flags each item, comments, and picks
an option for each decision, and read their answers back from it. Copy the
answers into the document's Answers section.

## When planning work

A spec or task list with a human review step names the review document's
path and contents, and says that the work stops until every item has an
answer.

## Related

- [markdown.md](markdown.md) - formatting conventions for the document
