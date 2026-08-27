# investment quiz
# version 4

# Import tkinter so we can create a GUI
import tkinter as tk

# Import messagebox so we can show warning messages
from tkinter import messagebox

# helps find image file
import os

# Import json so we can store user profiles and their quiz history
import json

# Import hashlib so we can store passwords as secure hashes
# instead of as plain readable text
import hashlib

# Import datetime so we can timestamp each saved result
import datetime

# Import matplotlib to create the investment allocation chart
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# checks if pygame is installed so music can be used
try:
    import pygame
    pygame_installed = True

except ImportError:
    pygame_installed = False


# constants

# This class stores constants used throughout the program.
# Keeping important values here makes the program easier to
# modify without searching through the whole program.

class AppConstants:

    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 800

    MIN_AGE = 16
    MAX_AGE = 18

    MIN_PASSWORD_LENGTH = 6

    LOW_INCOME_LIMIT = 30000
    HIGH_INCOME_LIMIT = 70000

    CONSERVATIVE_MAX_SCORE = 7
    MODERATE_MAX_SCORE = 11

    QUESTION_COUNT = 5
    OPTION_COUNT = 3

    PROGRESS_BAR_WIDTH = 400
    PROGRESS_BAR_HEIGHT = 22

    MUSIC_FILENAME = "music.mp3"
    PROFILE_FILENAME = "profiles.json"
    RESULTS_FILENAME = "investment_results.txt"

    WELCOME_IMAGE = "image.png"
    RESULTS_IMAGE = "results.png"

    BACKGROUND_FILENAMES = [
        "background.png",
        "background2.png",
        "background3.png",
        "background4.png"
    ]

    QUESTION_IMAGE_FILENAMES = [
        "question1.png",
        "question2.png",
        "question3.png",
        "question4.png",
        "question5.png"
    ]


# question class

# This class stores information about one quiz question.
#
# Each question has:
# "question" = the question itself.
# "options" = the possible answers.
# "scores" = the score for each answer.

class Question:

    def __init__(self, question, options, scores):

        self.question = question
        self.options = options
        self.scores = scores


# quiz engine

# This class contains the underlying quiz logic.
#
# It does NOT create Tkinter widgets.
# It does NOT display message boxes.
# It does NOT control the GUI.
#
# This means the quiz logic is separated from the GUI.

class QuizEngine:

    def __init__(self, questions):

        # Store the questions passed into the engine.
        self.questions = questions

        # Reset the quiz when the engine is created.
        self.reset()


    # reset function

    # This resets all quiz data so the quiz can be taken again.

    def reset(self):

        self.score = 0
        self.current_question = 0
        self.answer_history = []

        self.user_name = ""
        self.user_age = 0
        self.user_income = 0


    # set user details function

    # The GUI passes validated user details into the quiz engine.

    def set_user_details(
        self,
        name,
        age,
        income
    ):

        self.user_name = name
        self.user_age = age
        self.user_income = income


    # get current question function

    # Returns the current Question object.

    def get_current_question(self):

        return self.questions[
            self.current_question
        ]


    # get question count function

    # Returns the number of questions.

    def get_question_count(self):

        return len(
            self.questions
        )


    # get current question number function

    # Returns the question number in a user-friendly format.

    def get_current_question_number(self):

        return self.current_question + 1


    # answer question function

    # Adds the selected answer's score and stores the answer.

    def answer_question(self, answer_index):

        if answer_index < 0:
            return False

        if answer_index >= len(
            self.get_current_question().options
        ):
            return False

        question = self.get_current_question()

        self.score += question.scores[
            answer_index
        ]

        self.answer_history.append(
            answer_index
        )

        self.current_question += 1

        return True


    # go back function

    # Removes the previous answer and moves back one question.

    def go_back(self):

        if self.current_question <= 0:
            return False

        previous_answer = self.answer_history.pop()

        previous_question_index = (
            self.current_question - 1
        )

        self.score -= self.questions[
            previous_question_index
        ].scores[
            previous_answer
        ]

        self.current_question -= 1

        return True


    # quiz finished function

    # Returns True if all questions have been answered.

    def quiz_finished(self):

        return self.current_question >= len(
            self.questions
        )


    # get profile function

    # Calculates the user's risk profile from their score.

    def get_profile(self):

        if self.score <= AppConstants.CONSERVATIVE_MAX_SCORE:

            return "Conservative"

        elif self.score <= AppConstants.MODERATE_MAX_SCORE:

            return "Moderate"

        else:

            return "Growth"


    # get profile information function

    # Returns the result text and recommendations.

    def get_result_information(self):

        profile = self.get_profile()

        if profile == "Conservative":

            result = (
                "Risk Profile: Conservative\n"
                "You prefer lower levels of risk.\n\n"
                "Suggested investments:\n"
                "- Savings accounts\n"
                "- Term deposits\n"
                "- Bonds"
            )

        elif profile == "Moderate":

            result = (
                "Risk Profile: Moderate\n"
                "You are comfortable with some risk.\n\n"
                "Suggested investments:\n"
                "- Index funds\n"
                "- Balanced funds\n"
                "- Bonds"
            )

        else:

            result = (
                "Risk Profile: Growth\n"
                "You are comfortable with higher risk.\n\n"
                "Suggested investments:\n"
                "- Growth ETFs\n"
                "- Shares\n"
                "- Global index funds"
            )

        return result


    # get income suggestion function

    # Creates an additional recommendation based on income.

    def get_income_suggestion(self):

        if self.user_income < AppConstants.LOW_INCOME_LIMIT:

            return (
                "\n\nIncome Suggestion:\n"
                "Consider building your savings before making "
                "larger investments."
            )

        elif self.user_income <= AppConstants.HIGH_INCOME_LIMIT:

            return (
                "\n\nIncome Suggestion:\n"
                "Consider starting with smaller, diversified "
                "investments."
            )

        else:

            return (
                "\n\nIncome Suggestion:\n"
                "You may have more flexibility to consider a "
                "wider range of investments."
            )


    # get complete result function

    # This provides all information needed by the GUI.

    def get_complete_result(self):

        return (
            self.get_result_information()
            + self.get_income_suggestion()
        )


# profile manager

# This class handles JSON storage, profiles and passwords.
#
# It does NOT create Tkinter widgets.
# It does NOT control the quiz GUI.
#
# The GUI communicates with it through methods.

class ProfileManager:

    def __init__(self, profiles_path):

        self.profiles_path = profiles_path


    # hash password function

    # This converts a password into a secure hash.

    def hash_password(self, password):

        return hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest()


    # load profiles function

    # Loads profile information from the JSON file.

    def load_profiles(self):

        if not os.path.exists(
            self.profiles_path
        ):

            return {}


        try:

            with open(
                self.profiles_path,
                "r"
            ) as file:

                return json.load(file)


        except (
            OSError,
            json.JSONDecodeError
        ):

            return {}


    # save profiles function

    # Saves profile information to the JSON file.

    def save_profiles(self, profiles):

        try:

            with open(
                self.profiles_path,
                "w"
            ) as file:

                json.dump(
                    profiles,
                    file,
                    indent=2
                )

            return True

        except OSError:

            return False


    # ensure profile format function

    # Converts profiles from older versions into the new format.

    def ensure_profile_format(
        self,
        profiles,
        profile_key
    ):

        if profile_key in profiles and isinstance(
            profiles[profile_key],
            list
        ):

            profiles[profile_key] = {
                "password_hash": None,
                "history": profiles[profile_key]
            }

        return profiles


    # check login function

    # Checks whether a username and password are valid.
    #
    # This function returns information to the GUI rather than
    # displaying message boxes itself.

    def check_login(
        self,
        username,
        password
    ):

        profiles = self.load_profiles()

        profile_key = username.lower()

        profiles = self.ensure_profile_format(
            profiles,
            profile_key
        )


        # create a new profile

        if profile_key not in profiles:

            profiles[profile_key] = {
                "password_hash": self.hash_password(
                    password
                ),
                "history": []
            }

            if not self.save_profiles(
                profiles
            ):

                return False, "Could not save the new profile."

            return True, "New profile created."


        stored_hash = profiles[
            profile_key
        ].get(
            "password_hash"
        )


        # add a password to an older profile

        if stored_hash is None:

            profiles[
                profile_key
            ][
                "password_hash"
            ] = self.hash_password(
                password
            )

            if not self.save_profiles(
                profiles
            ):

                return False, "Could not save the profile."

            return True, "Password added to profile."


        # check existing password

        if stored_hash != self.hash_password(
            password
        ):

            return False, "Incorrect password."


        return True, "Login successful."


    # save quiz attempt function

    # Adds a completed quiz to the user's JSON history.

    def save_quiz_attempt(
        self,
        username,
        age,
        income,
        score,
        profile
    ):

        profiles = self.load_profiles()

        profile_key = username.lower()

        profiles = self.ensure_profile_format(
            profiles,
            profile_key
        )


        if profile_key not in profiles:

            profiles[profile_key] = {
                "password_hash": None,
                "history": []
            }


        entry = {
            "date": datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            ),
            "display_name": username,
            "age": age,
            "income": income,
            "score": score,
            "profile": profile
        }


        profiles[
            profile_key
        ][
            "history"
        ].append(
            entry
        )


        return self.save_profiles(
            profiles
        )


    # get history function

    # Returns a user's previous quiz attempts.

    def get_history(
        self,
        username,
        password
    ):

        profiles = self.load_profiles()

        profile_key = username.lower()

        profiles = self.ensure_profile_format(
            profiles,
            profile_key
        )


        if profile_key not in profiles:

            return False, "No history found.", []


        history = profiles[
            profile_key
        ].get(
            "history",
            []
        )


        if len(history) == 0:

            return False, "No history found.", []


        stored_hash = profiles[
            profile_key
        ].get(
            "password_hash"
        )


        if stored_hash is not None:

            if stored_hash != self.hash_password(
                password
            ):

                return False, "Incorrect password.", []


        return True, "History loaded.", history


# investment chart

# This class is responsible for creating the matplotlib chart.
#
# The chart receives the profile as data and does not calculate
# the user's risk profile itself.

class InvestmentChart:

    def __init__(self, parent):

        self.parent = parent
        self.canvas = None


    # show allocation chart function

    def show_allocation_chart(
        self,
        profile
    ):

        # Remove any previous chart.
        for widget in self.parent.winfo_children():

            widget.destroy()


        if profile == "Conservative":

            labels = [
                "Savings",
                "Bonds",
                "Index Funds"
            ]

            values = [
                50,
                35,
                15
            ]


        elif profile == "Moderate":

            labels = [
                "Index Funds",
                "Bonds",
                "Savings"
            ]

            values = [
                50,
                30,
                20
            ]


        else:

            labels = [
                "Growth ETFs",
                "Global Index Funds",
                "Shares"
            ]

            values = [
                45,
                35,
                20
            ]


        figure = Figure(
            figsize=(4, 2.2),
            dpi=100
        )


        axis = figure.add_subplot(
            111
        )


        axis.pie(
            values,
            labels=labels,
            autopct="%1.0f%%",
            startangle=90
        )


        axis.set_title(
            "Suggested Investment Allocation"
        )


        self.canvas = FigureCanvasTkAgg(
            figure,
            master=self.parent
        )


        self.canvas.draw()

        self.canvas.get_tk_widget().pack()


# gui

# This class is responsible for the Tkinter interface.
#
# It communicates with QuizEngine and ProfileManager through
# clearly defined methods.
#
# The quiz logic and profile storage are therefore separate
# from the GUI.

class InvestmentQuizGUI:

    def __init__(
        self,
        root,
        quiz_engine,
        profile_manager
    ):

        # Store the GUI window.
        self.root = root

        # Store the quiz engine interface.
        self.quiz_engine = quiz_engine

        # Store the profile manager interface.
        self.profile_manager = profile_manager


        # music settings

        self.music_available = pygame_installed
        self.music_playing = False


        # Find the program folder.

        self.folder = os.path.dirname(
            os.path.abspath(__file__)
        )


        # Create file paths.

        self.music_path = os.path.join(
            self.folder,
            AppConstants.MUSIC_FILENAME
        )

        self.results_path = os.path.join(
            self.folder,
            AppConstants.RESULTS_FILENAME
        )


        self.root.title(
            "Investment Recommendation Quiz"
        )

        self.root.geometry(
            str(
                AppConstants.WINDOW_WIDTH
            )
            + "x"
            + str(
                AppConstants.WINDOW_HEIGHT
            )
        )


        # images

        self.investment_image = None
        self.question_image = None
        self.results_image = None
        self.background_image = None


        # background paths

        self.background_paths = [
            os.path.join(
                self.folder,
                filename
            )
            for filename in AppConstants.BACKGROUND_FILENAMES
        ]


        self.current_background_index = 0


        # load background

        background_path = self.background_paths[
            self.current_background_index
        ]


        self.background_image = tk.PhotoImage(
            file=background_path
        )


        self.background_label = tk.Label(
            self.root,
            image=self.background_image
        )


        self.background_label.place(
            x=0,
            y=0,
            relwidth=1,
            relheight=1
        )


        self.background_label.lower()


        # title

        self.title = tk.Label(
            self.root,
            text="Investment Recommendation Quiz",
            font=("Arial", 20)
        )


        self.title.pack(
            pady=20
        )


        # welcome image

        image_path = os.path.join(
            self.folder,
            AppConstants.WELCOME_IMAGE
        )


        self.investment_image = tk.PhotoImage(
            file=image_path
        )


        self.investment_image = self.investment_image.subsample(
            3,
            3
        )


        self.image_label = tk.Label(
            self.root,
            image=self.investment_image
        )


        self.image_label.pack(
            pady=5
        )


        # results image

        self.results_image_path = os.path.join(
            self.folder,
            AppConstants.RESULTS_IMAGE
        )


        self.results_image_label = tk.Label(
            self.root
        )


        # user details

        self.name_label = tk.Label(
            self.root,
            text="Enter your name:",
            font=("Arial", 12)
        )

        self.name_label.pack()


        self.name_entry = tk.Entry(
            self.root,
            font=("Arial", 12)
        )

        self.name_entry.pack(
            pady=5
        )


        self.age_label = tk.Label(
            self.root,
            text="Enter your age:",
            font=("Arial", 12)
        )

        self.age_label.pack()


        self.age_entry = tk.Entry(
            self.root,
            font=("Arial", 12)
        )

        self.age_entry.pack(
            pady=5
        )


        self.income_label = tk.Label(
            self.root,
            text="Enter your annual income:",
            font=("Arial", 12)
        )

        self.income_label.pack()


        self.income_entry = tk.Entry(
            self.root,
            font=("Arial", 12)
        )

        self.income_entry.pack(
            pady=5
        )


        self.password_label = tk.Label(
            self.root,
            text="Enter a password (used to protect your results):",
            font=("Arial", 12)
        )

        self.password_label.pack()


        self.password_entry = tk.Entry(
            self.root,
            font=("Arial", 12),
            show="*"
        )

        self.password_entry.pack(
            pady=5
        )


        # question images

        self.question_image_paths = [
            os.path.join(
                self.folder,
                filename
            )
            for filename in AppConstants.QUESTION_IMAGE_FILENAMES
        ]


        self.question_image_label = tk.Label(
            self.root
        )


        # question label

        self.question_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 15),
            wraplength=500
        )


        self.progress_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 12)
        )


        # progress bar

        self.progress_bar = tk.Canvas(
            self.root,
            width=AppConstants.PROGRESS_BAR_WIDTH,
            height=AppConstants.PROGRESS_BAR_HEIGHT,
            bg="white",
            highlightthickness=1
        )


        self.progress_bar_text = self.progress_bar.create_text(
            AppConstants.PROGRESS_BAR_WIDTH // 2,
            AppConstants.PROGRESS_BAR_HEIGHT // 2,
            text="0%",
            font=("Arial", 10)
        )


        # answer variable

        self.choice = tk.IntVar(
            value=-1
        )


        # radio buttons

        self.buttons = []


        for index in range(
            AppConstants.OPTION_COUNT
        ):

            button = tk.Radiobutton(
                self.root,
                text="",
                variable=self.choice,
                value=index,
                font=("Arial", 12)
            )

            self.buttons.append(
                button
            )


        # navigation buttons

        self.button_frame = tk.Frame(
            self.root
        )


        self.next_button = tk.Button(
            self.button_frame,
            text="Next",
            command=self.next_question,
            font=("Arial", 12)
        )


        self.back_button = tk.Button(
            self.button_frame,
            text="Back",
            command=self.back_question,
            font=("Arial", 12)
        )


        # results buttons

        self.results_button_frame = tk.Frame(
            self.root
        )


        self.save_button = tk.Button(
            self.results_button_frame,
            text="Save Results",
            command=self.save_results,
            font=("Arial", 12)
        )


        self.restart_button = tk.Button(
            self.results_button_frame,
            text="Restart Quiz",
            command=self.restart_quiz,
            font=("Arial", 12)
        )


        # chart

        self.chart_frame = tk.Frame(
            self.root
        )


        self.chart = InvestmentChart(
            self.chart_frame
        )


        # disclaimer

        self.disclaimer = tk.Label(
            self.root,
            text="",
            font=("Arial", 8)
        )


        # start button

        self.start_button = tk.Button(
            self.root,
            text="Start Questions",
            command=self.get_user_details,
            font=("Arial", 12)
        )


        self.start_button.pack(
            pady=15
        )


        # history button

        self.view_history_button = tk.Button(
            self.root,
            text="View My History",
            command=self.view_history,
            font=("Arial", 11)
        )


        self.view_history_button.pack(
            pady=5
        )


        # music button

        self.music_button = tk.Button(
            self.root,
            text="Music: Off",
            command=self.toggle_music,
            font=("Arial", 11)
        )


        self.music_button.pack(
            side="bottom",
            pady=10
        )


        # background button

        self.background_button = tk.Button(
            self.root,
            text="Change Background",
            command=self.open_background_picker,
            font=("Arial", 11)
        )


        self.background_button.pack(
            side="bottom",
            pady=10
        )


    # user details function

    # Gets information from the GUI, validates it and then
    # passes the valid information to the QuizEngine.

    def get_user_details(self):

        name = self.name_entry.get().strip()
        age_text = self.age_entry.get().strip()
        income_text = self.income_entry.get().strip()
        password = self.password_entry.get().strip()


        if name == "":

            messagebox.showwarning(
                "No Name",
                "Please enter your name."
            )

            return


        if age_text == "":

            messagebox.showwarning(
                "No Age",
                "Please enter your age."
            )

            return


        try:

            age = int(
                age_text
            )

        except ValueError:

            messagebox.showwarning(
                "Invalid Age",
                "Please enter your age as a number."
            )

            return


        if age < AppConstants.MIN_AGE or age > AppConstants.MAX_AGE:

            messagebox.showwarning(
                "Invalid Age",
                "This quiz is designed for users aged "
                + str(AppConstants.MIN_AGE)
                + "-"
                + str(AppConstants.MAX_AGE)
                + "."
            )

            return


        if income_text == "":

            messagebox.showwarning(
                "No Income",
                "Please enter your annual income."
            )

            return


        try:

            income = float(
                income_text
            )

        except ValueError:

            messagebox.showwarning(
                "Invalid Income",
                "Please enter your income as a number."
            )

            return


        if income < 0:

            messagebox.showwarning(
                "Invalid Income",
                "Income cannot be negative."
            )

            return


        if password == "":

            messagebox.showwarning(
                "No Password",
                "Please enter a password."
            )

            return


        if len(password) < AppConstants.MIN_PASSWORD_LENGTH:

            messagebox.showwarning(
                "Password Too Short",
                "Your password must be at least "
                + str(AppConstants.MIN_PASSWORD_LENGTH)
                + " characters long."
            )

            return


        # Communicate with the profile manager.

        login_successful, login_message = (
            self.profile_manager.check_login(
                name,
                password
            )
        )


        if not login_successful:

            messagebox.showwarning(
                "Login Failed",
                login_message
            )

            return


        # Pass user information to the quiz engine.

        self.quiz_engine.set_user_details(
            name,
            age,
            income
        )


        self.hide_user_details()

        self.title.config(
            text="Welcome " + name + "!"
        )

        self.load_question()


    # hide user details function

    def hide_user_details(self):

        self.name_label.pack_forget()
        self.name_entry.pack_forget()

        self.age_label.pack_forget()
        self.age_entry.pack_forget()

        self.income_label.pack_forget()
        self.income_entry.pack_forget()

        self.password_label.pack_forget()
        self.password_entry.pack_forget()

        self.start_button.pack_forget()
        self.view_history_button.pack_forget()
        self.image_label.pack_forget()


    # load question function

    # Gets question data from QuizEngine and displays it.

    def load_question(self):

        self.choice.set(-1)

        question = self.quiz_engine.get_current_question()


        # load question image

        question_number = (
            self.quiz_engine.get_current_question_number()
        )


        self.question_image = tk.PhotoImage(
            file=self.question_image_paths[
                question_number - 1
            ]
        )


        self.question_image = self.question_image.subsample(
            2,
            2
        )


        self.question_image_label.config(
            image=self.question_image
        )


        self.question_image_label.pack(
            pady=5
        )


        # progress

        self.progress_label.config(
            text="Question "
            + str(question_number)
            + " of "
            + str(
                self.quiz_engine.get_question_count()
            )
        )


        self.progress_label.pack(
            pady=5
        )


        self.update_progress_bar()


        # question

        self.question_label.config(
            text=question.question,
            font=("Arial", 15)
        )


        self.question_label.pack(
            pady=15
        )


        # answers

        for index in range(
            len(question.options)
        ):

            self.buttons[index].config(
                text=question.options[index]
            )

            self.buttons[index].pack(
                anchor="w",
                padx=150
            )


        # navigation

        self.button_frame.pack(
            pady=20
        )


        if question_number > 1:

            self.back_button.pack(
                side="left",
                padx=10
            )

        else:

            self.back_button.pack_forget()


        self.next_button.pack(
            side="left",
            padx=10
        )


    # next question function

    # Gets the selected answer from the GUI and passes it
    # to QuizEngine.

    def next_question(self):

        selected_answer = self.choice.get()


        if selected_answer == -1:

            messagebox.showwarning(
                "No Answer",
                "Please select an answer."
            )

            return


        answer_accepted = (
            self.quiz_engine.answer_question(
                selected_answer
            )
        )


        if not answer_accepted:

            messagebox.showwarning(
                "Invalid Answer",
                "Please select a valid answer."
            )

            return


        if self.quiz_engine.quiz_finished():

            self.show_results()

        else:

            self.load_question()


    # back question function

    # Asks QuizEngine to move backwards.

    def back_question(self):

        if self.quiz_engine.go_back():

            self.load_question()


    # update progress bar function

    def update_progress_bar(self):

        self.progress_bar.delete(
            "bar"
        )


        percentage = int(
            (
                self.quiz_engine.get_current_question_number()
                /
                self.quiz_engine.get_question_count()
            )
            * 100
        )


        bar_width = int(
            AppConstants.PROGRESS_BAR_WIDTH
            * percentage
            / 100
        )


        self.progress_bar.create_rectangle(
            0,
            0,
            bar_width,
            AppConstants.PROGRESS_BAR_HEIGHT,
            fill="green",
            tags="bar"
        )


        self.progress_bar.itemconfig(
            self.progress_bar_text,
            text=str(percentage) + "%"
        )


        self.progress_bar.tag_raise(
            self.progress_bar_text
        )


        self.progress_bar.pack(
            pady=5
        )


    # results function

    # Gets the completed result from QuizEngine and displays it.

    def show_results(self):

        result = (
            self.quiz_engine.get_complete_result()
        )


        profile = (
            self.quiz_engine.get_profile()
        )


        self.question_label.config(
            text="Results for "
            + self.quiz_engine.user_name
            + "\n\n"
            + result,
            font=("Arial", 10)
        )


        self.question_label.pack(
            pady=2
        )


        # hide quiz controls

        for button in self.buttons:

            button.pack_forget()


        self.next_button.pack_forget()
        self.back_button.pack_forget()
        self.button_frame.pack_forget()
        self.progress_label.pack_forget()
        self.progress_bar.pack_forget()
        self.question_image_label.pack_forget()


        # disclaimer

        self.disclaimer.config(
            text="For educational purposes only. Not financial advice."
        )


        self.disclaimer.pack(
            side="bottom",
            pady=5
        )


        # results image

        self.results_image = tk.PhotoImage(
            file=self.results_image_path
        )


        self.results_image = self.results_image.subsample(
            3,
            3
        )


        self.results_image_label.config(
            image=self.results_image
        )


        self.results_image_label.pack(
            pady=0
        )


        # chart

        self.chart_frame.pack(
            pady=0
        )


        self.chart.show_allocation_chart(
            profile
        )


        # buttons

        self.results_button_frame.pack(
            pady=3
        )


        self.save_button.pack(
            side="left",
            padx=10
        )


        self.restart_button.pack(
            side="left",
            padx=10
        )


    # save results function

    # Saves the result to a text file and then asks the
    # ProfileManager to store the attempt in JSON.

    def save_results(self):

        profile = (
            self.quiz_engine.get_profile()
        )


        try:

            with open(
                self.results_path,
                "a"
            ) as file:

                file.write(
                    "Investment Quiz Result\n"
                )

                file.write(
                    "Name: "
                    + self.quiz_engine.user_name
                    + "\n"
                )

                file.write(
                    "Age: "
                    + str(
                        self.quiz_engine.user_age
                    )
                    + "\n"
                )

                file.write(
                    "Income: $"
                    + str(
                        self.quiz_engine.user_income
                    )
                    + "\n"
                )

                file.write(
                    "Result: "
                    + profile
                    + "\n"
                )

                file.write(
                    "Score: "
                    + str(
                        self.quiz_engine.score
                    )
                    + "\n"
                )

                file.write(
                    "------------------------------\n"
                )


        except OSError as error:

            messagebox.showerror(
                "Save Failed",
                "Your results could not be saved.\n\n"
                + str(error)
            )

            return


        # Pass the completed quiz information to ProfileManager.

        saved = (
            self.profile_manager.save_quiz_attempt(
                self.quiz_engine.user_name,
                self.quiz_engine.user_age,
                self.quiz_engine.user_income,
                self.quiz_engine.score,
                profile
            )
        )


        if not saved:

            messagebox.showerror(
                "Save Failed",
                "Your JSON profile history could not be saved."
            )

            return


        messagebox.showinfo(
            "Results Saved",
            "Your results have been saved successfully."
        )


    # view history function

    # Gets the username and password from the GUI and asks
    # ProfileManager for the user's history.

    def view_history(self):

        username = self.name_entry.get().strip()
        password = self.password_entry.get().strip()


        if username == "":

            messagebox.showwarning(
                "No Name",
                "Please enter your name first."
            )

            return


        if password == "":

            messagebox.showwarning(
                "No Password",
                "Please enter your password first."
            )

            return


        success, message, history = (
            self.profile_manager.get_history(
                username,
                password
            )
        )


        if not success:

            messagebox.showwarning(
                "History",
                message
            )

            return


        # history window

        history_window = tk.Toplevel(
            self.root
        )


        history_window.title(
            username + "'s History"
        )


        history_window.geometry(
            "450x400"
        )


        history_window.transient(
            self.root
        )


        heading = tk.Label(
            history_window,
            text="Past Results for " + username,
            font=("Arial", 13, "bold")
        )


        heading.pack(
            pady=10
        )


        text_frame = tk.Frame(
            history_window
        )


        text_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )


        scrollbar = tk.Scrollbar(
            text_frame
        )


        scrollbar.pack(
            side="right",
            fill="y"
        )


        history_text = tk.Text(
            text_frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            font=("Arial", 10)
        )


        history_text.pack(
            side="left",
            fill="both",
            expand=True
        )


        scrollbar.config(
            command=history_text.yview
        )


        # Display newest result first.

        entries = list(
            reversed(
                history
            )
        )


        for entry in entries:

            history_text.insert(
                "end",
                "Date: "
                + entry.get(
                    "date",
                    "Unknown"
                )
                + "\n"
            )


            history_text.insert(
                "end",
                "Age: "
                + str(
                    entry.get(
                        "age",
                        ""
                    )
                )
                + "\n"
            )


            history_text.insert(
                "end",
                "Income: $"
                + str(
                    entry.get(
                        "income",
                        ""
                    )
                )
                + "\n"
            )


            history_text.insert(
                "end",
                "Risk Profile: "
                + entry.get(
                    "profile",
                    ""
                )
                + "\n"
            )


            history_text.insert(
                "end",
                "Score: "
                + str(
                    entry.get(
                        "score",
                        ""
                    )
                )
                + "\n"
            )


            history_text.insert(
                "end",
                "-" * 40
                + "\n\n"
            )


        history_text.config(
            state="disabled"
        )


        close_button = tk.Button(
            history_window,
            text="Close",
            command=history_window.destroy,
            font=("Arial", 10)
        )


        close_button.pack(
            pady=10
        )


    # restart quiz function

    # Resets the underlying quiz engine and then resets the GUI.

    def restart_quiz(self):

        self.quiz_engine.reset()

        self.results_image_label.pack_forget()
        self.results_button_frame.pack_forget()
        self.chart_frame.pack_forget()
        self.question_image_label.pack_forget()
        self.question_label.pack_forget()
        self.progress_label.pack_forget()
        self.progress_bar.pack_forget()
        self.button_frame.pack_forget()
        self.disclaimer.pack_forget()


        for button in self.buttons:

            button.pack_forget()


        self.title.config(
            text="Investment Recommendation Quiz"
        )


        self.image_label.pack(
            pady=5
        )


        self.name_label.pack()
        self.name_entry.delete(
            0,
            tk.END
        )
        self.name_entry.pack(
            pady=5
        )


        self.age_label.pack()
        self.age_entry.delete(
            0,
            tk.END
        )
        self.age_entry.pack(
            pady=5
        )


        self.income_label.pack()
        self.income_entry.delete(
            0,
            tk.END
        )
        self.income_entry.pack(
            pady=5
        )


        self.password_label.pack()
        self.password_entry.delete(
            0,
            tk.END
        )
        self.password_entry.pack(
            pady=5
        )


        self.start_button.pack(
            pady=15
        )


        self.view_history_button.pack(
            pady=5
        )


    # music functions

    def start_music(self):

        if not self.music_available:

            messagebox.showinfo(
                "Music Not Available",
                "Background music is currently unavailable because "
                "pygame is not installed.\n\n"
                "To install pygame:\n\n"
                "1. Open Command Prompt or Terminal.\n"
                "2. Type:\n\n"
                "pip install pygame\n\n"
                "3. Press Enter.\n"
                "4. Restart this program."
            )

            return


        try:

            if not os.path.exists(
                self.music_path
            ):

                messagebox.showwarning(
                    "Music File Not Found",
                    "Could not find music.mp3.\n\n"
                    "Put music.mp3 in the same folder as "
                    "your Python program."
                )

                return


            if not self.music_playing:

                pygame.mixer.init()

                pygame.mixer.music.load(
                    self.music_path
                )

                pygame.mixer.music.play(
                    -1
                )

                self.music_playing = True

                self.music_button.config(
                    text="Music: On"
                )


        except Exception as error:

            messagebox.showwarning(
                "Music Error",
                "The music could not be played.\n\n"
                + str(error)
            )


    def stop_music(self):

        if self.music_available:

            if self.music_playing:

                try:

                    pygame.mixer.music.stop()

                    self.music_playing = False

                    self.music_button.config(
                        text="Music: Off"
                    )

                except Exception:

                    pass


    def toggle_music(self):

        if self.music_playing:

            self.stop_music()

        else:

            self.start_music()


    # background picker

    def open_background_picker(self):

        picker_window = tk.Toplevel(
            self.root
        )


        picker_window.title(
            "Choose a Background"
        )


        picker_window.geometry(
            "300x600"
        )


        picker_window.resizable(
            False,
            False
        )


        picker_window.transient(
            self.root
        )


        heading = tk.Label(
            picker_window,
            text="Select a background image:",
            font=("Arial", 13)
        )


        heading.pack(
            pady=10
        )


        self.background_previews = []


        for index, path in enumerate(
            self.background_paths
        ):

            if not os.path.exists(
                path
            ):

                missing_label = tk.Label(
                    picker_window,
                    text=AppConstants.BACKGROUND_FILENAMES[
                        index
                    ]
                    + " not found",
                    font=("Arial", 10)
                )


                missing_label.pack(
                    pady=5
                )

                continue


            preview_image = tk.PhotoImage(
                file=path
            )


            preview_image = preview_image.subsample(
                10,
                10
            )


            self.background_previews.append(
                preview_image
            )


            preview_button = tk.Button(
                picker_window,
                image=preview_image,
                text=AppConstants.BACKGROUND_FILENAMES[
                    index
                ],
                compound="top",
                font=("Arial", 9),
                command=lambda index=index:
                self.change_background(
                    index,
                    picker_window
                )
            )


            preview_button.pack(
                pady=8
            )


        close_button = tk.Button(
            picker_window,
            text="Close",
            command=picker_window.destroy,
            font=("Arial", 10)
        )


        close_button.pack(
            pady=10
        )


    # change background

    def change_background(
        self,
        index,
        picker_window
    ):

        chosen_path = self.background_paths[
            index
        ]


        try:

            self.background_image = tk.PhotoImage(
                file=chosen_path
            )


            self.background_label.config(
                image=self.background_image
            )


            self.current_background_index = index


        except Exception as error:

            messagebox.showwarning(
                "Background Error",
                "That background image could not be loaded.\n\n"
                + str(error)
            )

            return


        picker_window.destroy()


    # close program

    def close_program(self):

        self.stop_music()

        self.root.destroy()


# application class

# This class creates the objects required by the program.
#
# It connects the GUI to the underlying classes.

class InvestmentQuizApplication:

    def __init__(self):

        # Store all question data inside the application
        # instead of using a global variable.

        questions = [

            Question(
                "How long do you want to invest for?",
                [
                    "Less than 1 year",
                    "1-5 years",
                    "More than 5 years"
                ],
                [1, 2, 3]
            ),

            Question(
                "If your investment lost 20%, what would you do?",
                [
                    "Sell it",
                    "Wait",
                    "Buy more"
                ],
                [1, 2, 3]
            ),

            Question(
                "How much risk are you comfortable with?",
                [
                    "Low",
                    "Medium",
                    "High"
                ],
                [1, 2, 3]
            ),

            Question(
                "What is your main investment goal?",
                [
                    "Keep my money safe",
                    "Earn extra money",
                    "Grow my wealth"
                ],
                [1, 2, 3]
            ),

            Question(
                "How much investing experience do you have?",
                [
                    "None",
                    "Some",
                    "A lot"
                ],
                [1, 2, 3]
            )
        ]


        # Create the underlying quiz logic.

        self.quiz_engine = QuizEngine(
            questions
        )


        # Find the folder containing the program.

        folder = os.path.dirname(
            os.path.abspath(__file__)
        )


        # Create the profile manager.

        profiles_path = os.path.join(
            folder,
            AppConstants.PROFILE_FILENAME
        )


        self.profile_manager = ProfileManager(
            profiles_path
        )


        # Create the Tkinter window.

        self.root = tk.Tk()


        # Create the GUI and pass the underlying objects
        # into it through the constructor.

        self.gui = InvestmentQuizGUI(
            self.root,
            self.quiz_engine,
            self.profile_manager
        )


        # Make sure music stops when the user closes the program.

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.gui.close_program
        )


    # run function

    def run(self):

        self.root.mainloop()


# program entry point

# Create the application and run it.

application = InvestmentQuizApplication()

application.run()
