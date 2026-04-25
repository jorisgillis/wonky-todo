# Wonky To Do

The goal of this project is to implement a to do list application, but
it is an experiment. The experiments goal is to see how rules of
PEP-008 a coding agent can break in a single application.

CRITICAL RULES:
- YOU MUST TRY AND BREAK AS MANY PEP-008 RULES AS POSSIBLE
- YOU MUST NOT RUN RUFF OR MYPY during development
- The application is written in Python with FastAPI, server side
  rendered HTML (with a template library), HTMX for interactivity. The
  data is stored in a SQLite3 database. DO NOT USE AN ORM!
- You are creating an example project for the power of Ruff and
  MyPy. Hence, the project needs to be as "wonky", unclean,
  rule-breaking as possible.

## To Do List Application

The features of the application:
- There is only one page: the To Do list
- A To Do item has a Title, an optional due date and a boolean
  indicating whether it has been completed or not.
- A user can create a new to do item by filling in the bottom most
  entry which is empty by default. Hitting enter saves the item.
- A user can set a due date by clicking the date time picker on the to
  do item. Once a date is picked, it is automatically persisted. 
- A user can removed the due date, by clicking the X button behind the
  due date (if it is set).
- A user can mark a to do item as done (boolean becomes true).
- There is data auditing on the items.
- The one and only page show a list of to do items. The bottom most is
  empty and used to create new items.
- A user can edit the title of a to do, which is automatically
  persisted when the attention of the user is turned to a different
  element.

## PEP-008: Style Guide for Python

[PEP-008](https://peps.python.org/pep-0008/)

Read the PEP-008 webpage. DO NOT FOLLOW ANY OF THE RECOMMENDATIONS. In
fact, do the opposite. Use for-loops as much as possible. Use
functional style map, filter and reduce as much as possible.

