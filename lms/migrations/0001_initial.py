from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def seed_lms_content(apps, schema_editor):
    Subject = apps.get_model("lms", "Subject")
    Topic = apps.get_model("lms", "Topic")
    SubTopic = apps.get_model("lms", "SubTopic")
    Content = apps.get_model("lms", "Content")
    TopicTest = apps.get_model("lms", "TopicTest")
    Question = apps.get_model("lms", "Question")

    seed_data = {
        "Python": {
            "description": "Learn Python from beginner-friendly syntax through functions and object oriented design.",
            "topics": [
                {
                    "name": "Variables",
                    "subtopics": [
                        {
                            "name": "Getting started with variables",
                            "theory": "Variables store values so your program can reuse and update data while it runs.",
                            "example": "name = 'Aman'\nage = 21",
                            "explanation": "Python creates names dynamically. You do not declare a type before assigning a value.",
                            "sample_code": "name = 'Aman'\nage = 21\nprint(name)\nprint(age)",
                        }
                    ],
                    "questions": [
                        ("Which symbol assigns a value in Python?", "=", "==", ":", "->", 1),
                        ("What is the output type of age = 21?", "list", "int", "str", "float", 2),
                    ],
                },
                {
                    "name": "Loops",
                    "subtopics": [
                        {
                            "name": "For and while loops",
                            "theory": "Loops repeat blocks of logic and help process collections or repeated steps.",
                            "example": "for number in range(3):\n    print(number)",
                            "explanation": "A for loop iterates over a sequence, while a while loop runs until a condition becomes false.",
                            "sample_code": "for number in range(3):\n    print(number)\n\ncount = 0\nwhile count < 3:\n    print(count)\n    count += 1",
                        }
                    ],
                    "questions": [
                        ("Which loop is best for iterating through a list?", "switch", "for", "goto", "case", 2),
                        ("What does range(3) produce?", "0,1,2", "1,2,3", "3 only", "0,1,2,3", 1),
                    ],
                },
                {
                    "name": "Functions",
                    "subtopics": [
                        {
                            "name": "Defining reusable functions",
                            "theory": "Functions package logic into reusable blocks that can accept inputs and return outputs.",
                            "example": "def greet(name):\n    return f'Hello {name}'",
                            "explanation": "Use def to define a function. Parameters make the function flexible for different inputs.",
                            "sample_code": "def add(a, b):\n    return a + b\n\nprint(add(4, 5))",
                        }
                    ],
                    "questions": [
                        ("Which keyword defines a function in Python?", "func", "define", "def", "lambda", 3),
                        ("What does return do?", "prints to screen", "sends a value back", "starts a loop", "imports a module", 2),
                    ],
                },
                {
                    "name": "OOP",
                    "subtopics": [
                        {
                            "name": "Classes and objects",
                            "theory": "Object oriented programming models real concepts with classes, objects, attributes, and methods.",
                            "example": "class Student:\n    def __init__(self, name):\n        self.name = name",
                            "explanation": "A class is a blueprint. An object is the instance created from that blueprint.",
                            "sample_code": "class Student:\n    def __init__(self, name):\n        self.name = name\n\n    def intro(self):\n        return f'I am {self.name}'\n\nprint(Student('Riya').intro())",
                        }
                    ],
                    "questions": [
                        ("What does self refer to?", "The class", "The current object", "A global variable", "A module", 2),
                        ("Which method usually initializes a Python object?", "__start__", "__new__", "__init__", "__self__", 3),
                    ],
                },
            ],
        },
        "Java": {
            "description": "Build a strong Java foundation from syntax basics to collections and object oriented problem solving.",
            "topics": [
                {
                    "name": "Basics",
                    "subtopics": [
                        {
                            "name": "Java syntax and main method",
                            "theory": "Java programs are organized into classes and usually begin execution from the main method.",
                            "example": "public class Main {\n  public static void main(String[] args) {\n    System.out.println(\"Hello\");\n  }\n}",
                            "explanation": "The JVM looks for the main method as the entry point of a standalone Java program.",
                            "sample_code": "public class Main {\n  public static void main(String[] args) {\n    int age = 21;\n    System.out.println(age);\n  }\n}",
                        }
                    ],
                    "questions": [
                        ("Which method is the entry point in Java?", "run()", "main()", "start()", "init()", 2),
                        ("Which keyword creates a class?", "struct", "object", "class", "define", 3),
                    ],
                },
                {
                    "name": "OOP",
                    "subtopics": [
                        {
                            "name": "Encapsulation and objects",
                            "theory": "Java uses classes and objects to organize logic and data with encapsulation.",
                            "example": "class Car {\n  String brand;\n}",
                            "explanation": "Encapsulation protects data by controlling access through methods and modifiers.",
                            "sample_code": "class Car {\n  private String brand;\n  Car(String brand) { this.brand = brand; }\n  public String getBrand() { return brand; }\n}",
                        }
                    ],
                    "questions": [
                        ("Which access modifier hides fields from direct outside access?", "public", "private", "static", "void", 2),
                        ("An object is created from a?", "method", "package", "class", "loop", 3),
                    ],
                },
                {
                    "name": "Collections",
                    "subtopics": [
                        {
                            "name": "Lists and maps",
                            "theory": "Collections help manage groups of values such as ordered lists and key value pairs.",
                            "example": "List<String> names = new ArrayList<>();",
                            "explanation": "ArrayList stores ordered items, while HashMap stores values against keys.",
                            "sample_code": "List<String> names = new ArrayList<>();\nnames.add(\"Asha\");\nSystem.out.println(names.get(0));",
                        }
                    ],
                    "questions": [
                        ("Which class provides a resizable list?", "HashMap", "ArrayList", "Scanner", "Thread", 2),
                        ("Which collection stores key value pairs?", "List", "Queue", "Map", "Set only", 3),
                    ],
                },
            ],
        },
        "HTML": {
            "description": "Create semantic page structure with the core tags used in real web pages.",
            "topics": [
                {
                    "name": "Tags",
                    "subtopics": [
                        {
                            "name": "Headings, paragraphs, and links",
                            "theory": "HTML tags define the structure and meaning of page content.",
                            "example": "<h1>Welcome</h1>\n<p>Learn HTML</p>",
                            "explanation": "Use semantic tags so browsers and assistive tools can understand the page structure.",
                            "sample_code": "<h1>Course Title</h1>\n<p>This is a paragraph.</p>\n<a href=\"#\">Read more</a>",
                        }
                    ],
                    "questions": [
                        ("Which tag creates the largest heading?", "<h1>", "<head>", "<title>", "<p>", 1),
                        ("Which tag is used for a hyperlink?", "<p>", "<div>", "<a>", "<span>", 3),
                    ],
                },
                {
                    "name": "Layout",
                    "subtopics": [
                        {
                            "name": "Sections and page structure",
                            "theory": "Modern HTML layout uses semantic containers such as header, section, article, and footer.",
                            "example": "<header>Logo</header>\n<section>Content</section>",
                            "explanation": "Semantic layout makes content easier to style, navigate, and maintain.",
                            "sample_code": "<header>Header</header>\n<main>\n  <section>Hero</section>\n  <section>Features</section>\n</main>\n<footer>Footer</footer>",
                        }
                    ],
                    "questions": [
                        ("Which tag usually wraps the main page content?", "<footer>", "<main>", "<meta>", "<link>", 2),
                        ("Which tag is best for reusable standalone content?", "<article>", "<br>", "<img>", "<strong>", 1),
                    ],
                },
            ],
        },
        "CSS": {
            "description": "Style web pages with layout systems, spacing, typography, and responsive design.",
            "topics": [
                {
                    "name": "Layout",
                    "subtopics": [
                        {
                            "name": "Box model and spacing",
                            "theory": "CSS layout starts with the box model: content, padding, border, and margin.",
                            "example": ".card { padding: 16px; margin: 12px; }",
                            "explanation": "Padding adds inner spacing, while margin creates outer spacing between elements.",
                            "sample_code": ".card {\n  padding: 16px;\n  margin: 12px;\n  border: 1px solid #ccc;\n}",
                        }
                    ],
                    "questions": [
                        ("Which property adds inner spacing?", "margin", "padding", "display", "gap", 2),
                        ("Which property creates space outside the border?", "height", "padding", "margin", "position", 3),
                    ],
                },
                {
                    "name": "Flexbox",
                    "subtopics": [
                        {
                            "name": "Flexible row and column layouts",
                            "theory": "Flexbox aligns and distributes space across items inside a flexible container.",
                            "example": ".row { display: flex; gap: 12px; }",
                            "explanation": "You can control direction, alignment, wrapping, and spacing with a few focused properties.",
                            "sample_code": ".row {\n  display: flex;\n  justify-content: space-between;\n  align-items: center;\n}",
                        }
                    ],
                    "questions": [
                        ("Which property enables flexbox?", "display: grid", "display: inline", "display: flex", "position: flex", 3),
                        ("Which property aligns items on the cross axis?", "align-items", "justify-content", "flex-basis", "z-index", 1),
                    ],
                },
            ],
        },
        "JavaScript": {
            "description": "Add interactivity, logic, and browser-side behavior to web applications.",
            "topics": [
                {
                    "name": "Variables",
                    "subtopics": [
                        {
                            "name": "let, const, and basic values",
                            "theory": "JavaScript variables store values for dynamic behavior in the browser.",
                            "example": "const name = 'Dev';\nlet count = 1;",
                            "explanation": "Use const by default and let when a value needs to change.",
                            "sample_code": "const course = 'JavaScript';\nlet lessons = 5;\nconsole.log(course, lessons);",
                        }
                    ],
                    "questions": [
                        ("Which keyword is preferred for values that should not be reassigned?", "var", "const", "int", "define", 2),
                        ("Which function logs to the browser console?", "print()", "echo()", "console.log()", "log.console()", 3),
                    ],
                },
                {
                    "name": "Functions",
                    "subtopics": [
                        {
                            "name": "Reusable browser logic",
                            "theory": "Functions package behavior so code can react to user actions or repeated tasks.",
                            "example": "function greet(name) {\n  return `Hello ${name}`;\n}",
                            "explanation": "Functions can be declared, assigned to variables, or written as arrow functions.",
                            "sample_code": "const add = (a, b) => a + b;\nconsole.log(add(2, 3));",
                        }
                    ],
                    "questions": [
                        ("Which symbol appears in an arrow function?", "=>", "==", "::", "<>", 1),
                        ("A function can return a?", "value", "loop only", "CSS file", "HTML tag only", 1),
                    ],
                },
            ],
        },
    }

    for subject_order, (subject_name, subject_data) in enumerate(seed_data.items(), start=1):
        subject, _ = Subject.objects.get_or_create(
            name=subject_name,
            defaults={"description": subject_data["description"], "slug": subject_name.lower().replace(" ", "-")},
        )
        for topic_index, topic_data in enumerate(subject_data["topics"], start=1):
            topic, _ = Topic.objects.get_or_create(
                subject=subject,
                name=topic_data["name"],
                defaults={"order": topic_index, "slug": topic_data["name"].lower().replace(" ", "-")},
            )
            for subtopic_index, subtopic_data in enumerate(topic_data["subtopics"], start=1):
                subtopic, _ = SubTopic.objects.get_or_create(
                    topic=topic,
                    name=subtopic_data["name"],
                    defaults={"order": subtopic_index, "slug": subtopic_data["name"].lower().replace(" ", "-")},
                )
                Content.objects.get_or_create(
                    subtopic=subtopic,
                    theory=subtopic_data["theory"],
                    defaults={
                        "example": subtopic_data["example"],
                        "explanation": subtopic_data["explanation"],
                        "sample_code": subtopic_data["sample_code"],
                    },
                )

            test, _ = TopicTest.objects.get_or_create(
                topic=topic,
                title=f"{topic.name} Practice Test",
                defaults={"duration": 15},
            )
            if not test.questions.exists():
                for question_text, option1, option2, option3, option4, correct_option in topic_data["questions"]:
                    Question.objects.create(
                        test=test,
                        question_text=question_text,
                        option1=option1,
                        option2=option2,
                        option3=option3,
                        option4=option4,
                        correct_option=correct_option,
                    )


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Subject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True)),
                ("description", models.TextField(blank=True)),
                ("slug", models.SlugField(blank=True, max_length=140, unique=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Topic",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("order", models.PositiveIntegerField(default=1)),
                ("slug", models.SlugField(blank=True, max_length=170)),
                ("subject", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="topics", to="lms.subject")),
            ],
            options={"ordering": ["subject__name", "order", "name"], "unique_together": {("subject", "name")}},
        ),
        migrations.CreateModel(
            name="SubTopic",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("order", models.PositiveIntegerField(default=1)),
                ("slug", models.SlugField(blank=True, max_length=170)),
                ("topic", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="subtopics", to="lms.topic")),
            ],
            options={"ordering": ["topic__order", "order", "name"], "unique_together": {("topic", "name")}},
        ),
        migrations.CreateModel(
            name="TopicTest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("duration", models.PositiveIntegerField(help_text="Duration in minutes")),
                ("topic", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tests", to="lms.topic")),
            ],
            options={"ordering": ["topic__subject__name", "topic__order", "title"]},
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question_text", models.TextField()),
                ("option1", models.CharField(max_length=255)),
                ("option2", models.CharField(max_length=255)),
                ("option3", models.CharField(max_length=255)),
                ("option4", models.CharField(max_length=255)),
                ("correct_option", models.PositiveSmallIntegerField(choices=[(1, "Option 1"), (2, "Option 2"), (3, "Option 3"), (4, "Option 4")])),
                ("test", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="lms.topictest")),
            ],
            options={"ordering": ["id"]},
        ),
        migrations.CreateModel(
            name="Content",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("theory", models.TextField()),
                ("example", models.TextField(blank=True)),
                ("explanation", models.TextField(blank=True)),
                ("sample_code", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("subtopic", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="contents", to="lms.subtopic")),
            ],
            options={"ordering": ["subtopic__order", "id"]},
        ),
        migrations.CreateModel(
            name="Batch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("start_date", models.DateField()),
                ("subject", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="batches", to="lms.subject")),
            ],
            options={"ordering": ["subject__name", "start_date", "name"]},
        ),
        migrations.CreateModel(
            name="ScheduledExam",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("batch", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="scheduled_exams", to="lms.batch")),
                ("subject", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="scheduled_exams", to="lms.subject")),
                ("topic_test", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="scheduled_instances", to="lms.topictest")),
            ],
            options={"ordering": ["start_time"]},
        ),
        migrations.CreateModel(
            name="TestResult",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score", models.PositiveIntegerField(default=0)),
                ("total", models.PositiveIntegerField(default=0)),
                ("completed_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("test", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="results", to="lms.topictest")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="topic_test_results", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-completed_at"]},
        ),
        migrations.CreateModel(
            name="UserAnswer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("selected_option", models.PositiveSmallIntegerField(choices=[(1, "Option 1"), (2, "Option 2"), (3, "Option 3"), (4, "Option 4")])),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="user_answers", to="lms.question")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="topic_user_answers", to=settings.AUTH_USER_MODEL)),
            ],
            options={"unique_together": {("user", "question")}},
        ),
        migrations.CreateModel(
            name="UserProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("completed", models.BooleanField(default=False)),
                ("score", models.PositiveIntegerField(default=0)),
                ("topic", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="progress_records", to="lms.topic")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="topic_progress", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["topic__subject__name", "topic__order"], "unique_together": {("user", "topic")}},
        ),
        migrations.CreateModel(
            name="CodeSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("language", models.CharField(choices=[("python", "Python"), ("java", "Java"), ("javascript", "JavaScript")], default="python", max_length=20)),
                ("code", models.TextField(blank=True)),
                ("output", models.TextField(blank=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("subtopic", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="code_submissions", to="lms.subtopic")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="code_submissions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-updated_at"], "unique_together": {("user", "subtopic")}},
        ),
        migrations.RunPython(seed_lms_content, migrations.RunPython.noop),
    ]
