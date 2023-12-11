# SimpleScheduler
Simple code to order tasks on your to-do lists based on shortest-duration time, weighed by importance and time until the due date. Adapted from the chapter in Algorithms to Live By on scheduling.

## Dependencies

I originally designed this to work across devices, but now it only runs locally on Macs with the Apple Silicon chip, since it is using the new MLX package.

To install the necessary packages, run 

```
pip install mlx
pip install pandas
pip install numpy
```

I'm running the code on Python 3.11.3, but it should work on any version >= 3.8, since that's what MLX requires.

## Viewing tasks

To view the tasks you should most immediately do, run the code below

```
python scheduler.py
```

To view all tasks on your list sorted by the order you should complete them, run the code below and follow the corresponding prompts

```
python scheduler.py --viewTasks
```

## Adding/Removing tasks
To add tasks to your to-do list, run the code below and follow the corresponding prompts

```
python scheduler.py --addTask
```

To remove a task from your to-do list, run the code below and follow the corresponding prompts

```
python scheduler.py --removeTask
```

Both commands will add or remove the task you specify and then display the tasks you should complete next on your to-do list, according to the viewing option specified.
