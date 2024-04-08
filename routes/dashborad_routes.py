from flask import Flask, render_template, redirect, Blueprint, request, jsonify, session, flash
from datetime import datetime, timedelta
from mysqlconnection import connectToMySQL   # import the function that will return an instance of a connection
from routes.user_routes import check_user_id, get_my_team, signout  # Import the check_user_id function from user_routes.py
from validations.validations import *
import json

# app = Flask(__name__, static_folder='../static', template_folder='../templates')
# app.secret_key = 'your_secret_key_here'


app = Blueprint('dashboard_app', __name__)


# Render dashboard page.
@app.route("/dashboard")
def render_dashboard_page():
    checked_user = check_user_id()
    if checked_user:
        my_team_data_response  = get_my_team()
        my_team_data = json.loads(my_team_data_response.data)
        return render_template("dashboard/dashboard.html", has_team = my_team_data['has_team'], the_supervisor = my_team_data['the_supervisor'], the_team = my_team_data['the_team'], checked_user=checked_user)
    return redirect("/sign_out")


# Get all posts with their data to view them on the dashboard page.
@app.route("/dashboard/get_posts/<int:posts_number>/<int:posts_offset>")
@app.route("/dashboard/get_posts")
def rend(posts_number=3, posts_offset=0):
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        # Get the latest 3 posts.
        get_posts_query = """
            SELECT 
                p.post_id, p.caption, p.created_at, p.updated_at, 
                u.user_id AS author_user_id, CONCAT(u.first_name, ' ', u.last_name) AS author_full_name, u.image_id AS author_image_id, u.job_title AS author_job_title,
                COUNT(DISTINCT c.comment_id) + COUNT(DISTINCT r.reply_id) AS comments_count,
                COUNT(DISTINCT l.like_id) AS likes_count,
                MAX(CASE WHEN l.user_id = %(user_id_from_session)s THEN true ELSE false END) AS is_liker,
                (p.user_id = %(user_id_from_session)s) AS is_owner
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            LEFT JOIN comments c ON p.post_id = c.post_id
            LEFT JOIN replies r ON c.comment_id = r.comment_id
            LEFT JOIN likes l ON p.post_id = l.reference_id AND l.reference_table = 'posts'
            GROUP BY p.post_id, p.caption, p.created_at, p.updated_at, u.user_id, u.image_id, u.job_title
            ORDER BY p.updated_at DESC
            LIMIT %(posts_number_from_URL)s OFFSET %(posts_offset_from_URL)s;
        """
        data = {
            'user_id_from_session': session['user_id'],
            'posts_number_from_URL': posts_number,
            'posts_offset_from_URL': posts_offset
        }
        posts = mysql.query_db(get_posts_query, data)

        # Convert timestamps into human readable strings.
        for post in posts:
            post['created_at'] = format_time_difference_for_post(post['created_at'])
            post['updated_at'] = format_time_difference_for_post(post['updated_at'])
            post['author_job_title'] = replace_job_title(post['author_job_title'])

        return jsonify(posts)

    # The signout will redirect to the "/" route.
    return signout()


# Render view_post page.
@app.route("/dashboard/<post_id>")
def render_view_post_page(post_id):
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        # Get the data of the post and the data of the author.
        post_query = """
            SELECT 
                p.post_id, p.caption, p.created_at, p.updated_at, 
                u.user_id AS author_user_id, CONCAT(u.first_name, ' ', u.last_name) AS author_full_name, u.image_id AS author_image_id, u.job_title AS author_job_title,
                COUNT(DISTINCT c.comment_id) + COUNT(DISTINCT r.reply_id) AS comments_count,
                COUNT(DISTINCT l.like_id) AS likes_count,
                MAX(CASE WHEN l.user_id = %(user_id_from_session)s THEN true ELSE false END) AS is_liker,
                (p.user_id = %(user_id_from_session)s) AS is_owner
            FROM posts p
            JOIN users u ON p.user_id = u.user_id
            LEFT JOIN comments c ON p.post_id = c.post_id
            LEFT JOIN replies r ON c.comment_id = r.comment_id
            LEFT JOIN likes l ON p.post_id = l.reference_id AND l.reference_table = 'posts'
            WHERE p.post_id = %(post_id_from_URL)s
            GROUP BY p.post_id, p.caption, p.created_at, p.updated_at, u.user_id, u.image_id, u.job_title;
        """
        data = {
            'post_id_from_URL': post_id,
            'user_id_from_session': session['user_id']
        }
        post = mysql.query_db(post_query, data)[0]

        post['created_at'] = format_time_difference_for_post(post['created_at'])
        post['updated_at'] = format_time_difference_for_post(post['updated_at'])
        post['author_job_title'] = replace_job_title(post['author_job_title'])

        return render_template('dashboard/view_post.html', the_post=post, checked_user=checked_user)
    return redirect("/sign_out")



# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Methods to get media/comments/replies of a specefic post, they are used in the dashboard page.

# Retrieve the media of the selected post.
@app.route("/dashboard/get_media_of_post/<post_id>")
def get_media_of_post(post_id):
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        media_query = """
            SELECT media_id, name AS media_name, type AS media_type
            FROM media
            WHERE reference_id = %(post_id_form_URL)s
                AND reference_table = 'posts';
        """
        data = { 'post_id_form_URL': post_id }
        media = mysql.query_db(media_query, data)

        return jsonify(media)

    # The signout will redirect to the "/" route.
    return signout()


# Retrieve the comments and their data of the selected post.
@app.route("/dashboard/get_comments_of_post/<post_id>")
def get_comments_of_post(post_id):
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        comments_query = """
            SELECT 
                c.comment_id, c.caption, c.created_at, c.updated_at,
                u.user_id AS author_user_id, CONCAT(u.first_name, ' ', u.last_name) AS author_full_name, u.image_id AS author_image_id, u.job_title AS author_job_title,
                COUNT(DISTINCT r.reply_id) AS replies_count,
                COUNT(DISTINCT l.like_id) AS likes_count,
                m.media_id, m.name AS media_name, m.type AS media_type,
                MAX(CASE WHEN l.user_id = %(user_id_from_session)s THEN true ELSE false END) AS is_liker,
                (c.user_id = %(user_id_from_session)s) AS is_owner
            FROM comments c 
            LEFT JOIN users u ON c.user_id = u.user_id
            LEFT JOIN replies r ON c.comment_id = r.comment_id
            LEFT JOIN likes l ON c.comment_id = l.reference_id AND l.reference_table = 'comments'
            LEFT JOIN media m ON c.comment_id = m.reference_id AND m.reference_table = 'comments'
            WHERE c.post_id = %(post_id_form_URL)s
            GROUP BY c.comment_id, u.user_id, u.first_name, u.last_name, u.image_id, u.job_title, m.media_id, m.name, m.type
            ORDER BY c.created_at DESC;
        """
        data = {
            'post_id_form_URL': post_id,
            'user_id_from_session': session['user_id']
        }
        comments = mysql.query_db(comments_query, data)
        for comment in comments:
            comment['created_at'] = format_time_difference_for_comments_and_replies(comment['created_at'])
            comment['updated_at'] = format_time_difference_for_comments_and_replies(comment['updated_at'])
            comment['author_job_title'] = replace_job_title(comment['author_job_title'])

        return jsonify(comments)

    # The signout will redirect to the "/" route.
    return signout()


# Retrieve the replies and their data of the selected comment.
@app.route("/dashboard/get_replies_of_comment/<comment_id>")
def get_replies_of_comment(comment_id):
    checked_user = check_user_id()
    if checked_user:
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        replies_query = """
            SELECT 
                r.reply_id, r.caption, r.created_at, r.updated_at,
                u.user_id AS author_user_id, CONCAT(u.first_name, ' ', u.last_name) AS author_full_name, u.image_id AS author_image_id, u.job_title AS author_job_title,
                COUNT(DISTINCT l.like_id) AS likes_count,
                m.media_id, m.name AS media_name, m.type AS media_type,
                MAX(CASE WHEN l.user_id = %(user_id_from_session)s THEN true ELSE false END) AS is_liker,
                (r.user_id = %(user_id_from_session)s) AS is_owner
            FROM replies r 
            LEFT JOIN users u ON r.user_id = u.user_id
            LEFT JOIN likes l ON r.reply_id = l.reference_id AND l.reference_table = 'replies'
            LEFT JOIN media m ON r.reply_id = m.reference_id AND m.reference_table = 'replies'
            WHERE r.comment_id = %(comment_id_form_URL)s
            GROUP BY r.reply_id, u.user_id, u.first_name, u.last_name, u.image_id, u.job_title, m.media_id, m.name, m.type
            ORDER BY r.created_at;
        """
        data = {
            'comment_id_form_URL': comment_id,
            'user_id_from_session': session['user_id']
        }
        replies = mysql.query_db(replies_query, data)
        for reply in replies:
            reply['created_at'] = format_time_difference_for_comments_and_replies(reply['created_at'])
            reply['updated_at'] = format_time_difference_for_comments_and_replies(reply['updated_at'])
            reply['author_job_title'] = replace_job_title(reply['author_job_title'])

        return jsonify(replies)

    # The signout will redirect to the "/" route.
    return signout()



# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ADD/DELETE like on a post/comment/reply methods.

# Handle the like button of the post.
@app.route("/dashboard/like_post/<post_id>", methods=["POST"])
def like_post(post_id):
    checked_user = check_user_id()
    if checked_user:
        data = {
            'post_id_from_request': post_id,
            'user_id_from_session': session['user_id']
        }

        # Check if the user has already liked the post
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        is_liker_query = """
            SELECT COUNT(like_id) AS like_count
            FROM likes
            WHERE user_id = %(user_id_from_session)s
            AND reference_id = %(post_id_from_request)s 
            AND reference_table = 'posts';
        """
        is_liker = mysql.query_db(is_liker_query, data)[0]['like_count']

        if is_liker:
            # Unlike the post
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            unlike_query = """
                DELETE FROM likes 
                WHERE user_id = %(user_id_from_session)s 
                    AND reference_id = %(post_id_from_request)s 
                    AND reference_table = 'posts';
            """
            mysql.query_db(unlike_query, data)
        else:
            # Like the post
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            like_query = """
                INSERT INTO likes (user_id, reference_id, reference_table)
                VALUES (%(user_id_from_session)s, %(post_id_from_request)s, 'posts');
            """
            mysql.query_db(like_query, data)

        return jsonify(is_liker=is_liker)

    # The signout will redirect to the "/" route.
    return signout()


# Handle the like button of the comment.
@app.route("/dashboard/like_comment/<comment_id>", methods=["POST"])
def like_comment(comment_id):
    checked_user = check_user_id()
    if checked_user:
        data = {
            'comment_id_from_request': comment_id,
            'user_id_from_session': session['user_id']
        }

        # Check if the user has already liked the comment
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        is_liker_query = """
            SELECT COUNT(like_id) AS like_count
            FROM likes
            WHERE user_id = %(user_id_from_session)s
            AND reference_id = %(comment_id_from_request)s 
            AND reference_table = 'comments';
        """
        is_liker = mysql.query_db(is_liker_query, data)[0]['like_count']

        if is_liker:
            # Unlike the comment
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            unlike_query = """
                DELETE FROM likes 
                WHERE user_id = %(user_id_from_session)s 
                    AND reference_id = %(comment_id_from_request)s 
                    AND reference_table = 'comments';
            """
            mysql.query_db(unlike_query, data)
        else:
            # Like the comment
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            like_query = """
                INSERT INTO likes (user_id, reference_id, reference_table)
                VALUES (%(user_id_from_session)s, %(comment_id_from_request)s, 'comments');
            """
            mysql.query_db(like_query, data)

        return jsonify(is_liker=is_liker)

    # The signout will redirect to the "/" route.
    return signout()


# Handle the like button of the reply.
@app.route("/dashboard/like_reply/<reply_id>", methods=["POST"])
def like_reply(reply_id):
    checked_user = check_user_id()
    if checked_user:
        data = {
            'reply_id_from_request': reply_id,
            'user_id_from_session': session['user_id']
        }

        # Check if the user has already liked the reply
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        is_liker_query = """
            SELECT COUNT(like_id) AS like_count
            FROM likes
            WHERE user_id = %(user_id_from_session)s
            AND reference_id = %(reply_id_from_request)s 
            AND reference_table = 'replies';
        """
        is_liker = mysql.query_db(is_liker_query, data)[0]['like_count']

        if is_liker:
            # Unlike the reply
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            unlike_query = """
                DELETE FROM likes 
                WHERE user_id = %(user_id_from_session)s 
                    AND reference_id = %(reply_id_from_request)s 
                    AND reference_table = 'replies';
            """
            mysql.query_db(unlike_query, data)
        else:
            # Like the reply
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            like_query = """
                INSERT INTO likes (user_id, reference_id, reference_table)
                VALUES (%(user_id_from_session)s, %(reply_id_from_request)s, 'replies');
            """
            mysql.query_db(like_query, data)

        return jsonify(is_liker=is_liker)

    # The signout will redirect to the "/" route.
    return signout()


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////

# This function converts a timestamp to a human-readable time difference string, 
# displaying it as "X seconds/minutes/hours ago" for recent times, 
# "Yesterday at HH:MM" for yesterday, or "DD Month at HH:MM" for dates within the same year,
# and "DD Month YYYY at HH:MM" for dates in different years.
def format_time_difference_for_post(timestamp):
    # Calculate the time difference
    now = datetime.now()
    time_difference = now - timestamp
    # If still in the same day
    if timestamp.date() == now.date():
        if time_difference.total_seconds() < 60:
            return f"{int(time_difference.seconds)} seconds ago"
        elif time_difference.total_seconds() < 3600:
            return f"{int(time_difference.seconds / 60)} minutes ago"
        else:
            return f"{int(time_difference.seconds / 3600)} hours ago"
    # If in the next day
    elif timestamp.date() == (now - timedelta(days=1)).date():
        return f"Yesterday at {timestamp.strftime('%H:%M')}"
    # If in the same year
    elif timestamp.year == now.year:
        return timestamp.strftime('%d %B at %H:%M')
    # If not in the same year
    else:
        return timestamp.strftime('%d %B %Y at %H:%M')


# The function formats a timestamp into a human-readable time difference string. 
# It expresses recent times as "X seconds/minutes/hours ago", 
# "Yesterday at HH:MM" for the previous day, "X days ago" for days within the same week,
# and "X weeks ago" for older dates.
def format_time_difference_for_comments_and_replies(timestamp):
    now = datetime.now()
    time_difference = now - timestamp

    if time_difference.total_seconds() < 60:
        return f"{int(time_difference.seconds)} {'sec' if int(time_difference.seconds) == 1 else 'secs'}"
    elif time_difference.total_seconds() < 3600:
        return f"{int(time_difference.seconds / 60)} {'min' if int(time_difference.seconds / 60) == 1 else 'mins'}"
    elif time_difference.total_seconds() < 86400:
        return f"{int(time_difference.seconds / 3600)} {'hr' if int(time_difference.seconds / 3600) == 1 else 'hrs'}"
    elif time_difference.total_seconds() < 604800:
        return f"{int(time_difference.days)} {'day' if int(time_difference.days) == 1 else 'days'}"
    else:
        weeks = int(time_difference.days / 7)
        return f"{weeks} {'week' if weeks == 1 else 'weeks'}"


# replace the job_title and gender from the database with correct values.
def replace_job_title(job_title_id):
    job_titles = {
        1: "adminstrator",
        2: "manager",
        3: "worker"
    }
    return job_titles[job_title_id]


# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ADD new post/comment/reply methods.

# Adding new post to database.
@app.route("/dashboard/add_new_post", methods=["POST"])
def add_new_post():
    checked_user = check_user_id()
    if checked_user:
        # Passing the data from the form to the validation method to validate it first then return the valid values from it.
        data, validation_errors = validate_add_new_post_method(request.form, request.files)

        if validation_errors:
            return signout()

        # Add post to the database.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        add_post_query = """
            INSERT INTO posts (caption, user_id)
            VALUES (
                %(caption_from_form)s,
                %(user_id_from_session)s
            );
        """
        data['post_id'] = mysql.query_db(add_post_query, data)

        # If the post got media with it: 
        if 'added_media_names' in data:
            # Add the new media files from the database.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            # Construct the INSERT INTO query with properly formatted tuples.
            add_new_post_media_query = """
                INSERT INTO media (name, type, reference_table, reference_id) VALUES {}
            """.format(', '.join(["('{}', '{}', 'posts', %(post_id)s)".format(name, media_type) for name, media_type in data['added_media_names'].items()]))
            # Execute the query
            mysql.query_db(add_new_post_media_query, data)

        return redirect('/dashboard')

    # The signout will redirect to the "/" route.
    return signout()


# Adding new comment to database.
@app.route("/dashboard/add_new_comment", methods=["POST"])
def add_new_comment():
    checked_user = check_user_id()
    if checked_user:
        # Passing the data from the form to the validation method to validate it first then return the valid values from it.
        data, validation_errors = validate_add_new_comment_method(request.form, request.files)

        if validation_errors:
            return signout()

        # Add comment to the database.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        add_comment_query = """
            INSERT INTO comments (caption, post_id, user_id)
            VALUES (
                %(caption_from_form)s,
                %(post_id_from_form)s,
                %(user_id_from_session)s
            );
        """
        data['comment_id'] = mysql.query_db(add_comment_query, data)

        # If the comment got media with it: 
        if 'media_name' in data:
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            add_media_query = """
                INSERT INTO media (name, reference_id, reference_table, type)
                VALUES (
                    %(media_name)s,
                    %(comment_id)s,
                    'comments',
                    %(media_type)s
                );
            """
            mysql.query_db(add_media_query, data)

        return jsonify(success=True)

    # The signout will redirect to the "/" route.
    return signout()



    # ////////////////////////////////////////////////////////////////////////////////////////////////////////////////


# Adding new reply to database.
@app.route("/dashboard/add_new_reply", methods=["POST"])
def add_new_reply():
    checked_user = check_user_id()
    if checked_user:
        # Passing the data from the form to the validation method to validate it first then return the valid values from it.
        data, validation_errors = validate_add_new_reply_method(request.form, request.files)

        if validation_errors:
            return signout()

        # Add comment to the database.
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        add_reply_query = """
            INSERT INTO replies (caption, comment_id, user_id)
            VALUES (
                %(caption_from_form)s,
                %(comment_id_from_form)s,
                %(user_id_from_session)s
            );
        """
        data['reply_id'] = mysql.query_db(add_reply_query, data)

        # If the comment got media with it: 
        if 'media_name' in data:
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            add_media_query = """
                INSERT INTO media (name, reference_id, reference_table, type)
                VALUES (
                    %(media_name)s,
                    %(reply_id)s,
                    'replies',
                    %(media_type)s
                );
            """
            mysql.query_db(add_media_query, data)

        return jsonify(success=True)

    # The signout will redirect to the "/" route.
    return signout()



# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# UPDATE post/comment/reply methods.

# Update post in the database.
@app.route("/dashboard/update_post", methods=["POST"])
def update_post():
    checked_user = check_user_id()
    if checked_user:
        # Check if the logged in user is the author of the post.
        data = { 'updated_post_id': request.form.get('updated_post_id') }
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        post_author_id_query = """
            SELECT user_id FROM posts WHERE post_id = %(updated_post_id)s;
        """
        post_author_id = mysql.query_db(post_author_id_query, data)[0]['user_id']
        if session['user_id'] == post_author_id:
            # Passing the data from the form to the validation method to validate it first then return the valid values from it.
            data, validation_errors = validate_update_post_method(request.form, request.files)

            if validation_errors:
                return signout()

            # Update the post.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            update_post_query = """
                UPDATE posts
                SET caption = %(updated_post_caption)s
                WHERE post_id = %(updated_post_id)s;
            """
            mysql.query_db(update_post_query, data)

            url = request.referrer 
            # Redirect to the same page of the post to refresch it.
            return redirect(url)

    # The signout will redirect to the "/" route.
    return signout()


# Update comment in the database.
@app.route("/dashboard/update_comment", methods=["POST"])
def update_comment():
    checked_user = check_user_id()
    if checked_user:
        # Check if the logged in user is the author of the comment.
        data = { 'updated_comment_id': request.form.get('updated_comment_id') }
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        comment_author_id_query = """
            SELECT user_id FROM comments WHERE comment_id = %(updated_comment_id)s;
        """
        comment_author_id = mysql.query_db(comment_author_id_query, data)[0]['user_id']
        if session['user_id'] == comment_author_id:
            # Passing the data from the form to the validation method to validate it first then return the valid values from it.
            data, validation_errors = validate_update_comment_method(request.form, request.files)

            if validation_errors:
                return signout()

            # Update the comment.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            update_comment_query = """
                UPDATE comments
                SET caption = %(updated_comment_caption)s, updated_at = NOW()
                WHERE comment_id = %(updated_comment_id)s;
            """
            mysql.query_db(update_comment_query, data)

            return jsonify(success=True)

    # The signout will redirect to the "/" route.
    return signout()


# Update reply in the database.
@app.route("/dashboard/update_reply", methods=["POST"])
def update_reply():
    checked_user = check_user_id()
    if checked_user:
        # Check if the logged in user is the author of the reply.
        data = { 'updated_reply_id': request.form.get('updated_reply_id') }
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        reply_author_id_query = """
            SELECT user_id FROM replies WHERE reply_id = %(updated_reply_id)s;
        """
        reply_author_id = mysql.query_db(reply_author_id_query, data)[0]['user_id']
        if session['user_id'] == reply_author_id:
            # Passing the data from the form to the validation method to validate it first then return the valid values from it.
            data, validation_errors = validate_update_reply_method(request.form, request.files)

            if validation_errors:
                return signout()

            # Update the reply.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            update_reply_query = """
                UPDATE replies
                SET caption = %(updated_reply_caption)s, updated_at = NOW()
                WHERE reply_id = %(updated_reply_id)s;
            """
            mysql.query_db(update_reply_query, data)

            return jsonify(success=True)

    # The signout will redirect to the "/" route.
    return signout()



# //////////////////////////////////////////////////////////////////////////////////////////////////////////////
# DELETE post/comment/reply methods.

# Delete a post with it's comments & replies.
@app.route("/dashboard/<post_id>/delete_post", methods=["DELETE"])
def delete_post(post_id):
    checked_user = check_user_id()
    if checked_user:
        # Check if the logged in user is the author of the post.
        data = { 'post_id_from_URL': post_id }
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        post_author_id_query = """
            SELECT user_id FROM posts WHERE post_id = %(post_id_from_URL)s;
        """
        post_author_id = mysql.query_db(post_author_id_query, data)[0]['user_id']
        if session['user_id'] == post_author_id:
            # Delete all the media related to the post, either they are for the post itself or for it's comments & replies.
            # If you want to keep them, although the post is deleted just comment out this step and query.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            all_related_media_of_post_query = """
                SELECT DISTINCT m.name, m.type, m.reference_table
                FROM posts p
                LEFT JOIN comments c ON p.post_id = c.post_id
                LEFT JOIN replies r ON c.comment_id = r.comment_id
                LEFT JOIN media m ON 
                    (p.post_id = m.reference_id AND m.reference_table = 'posts') OR
                    (c.comment_id = m.reference_id AND m.reference_table = 'comments') OR
                    (r.reply_id = m.reference_id AND m.reference_table = 'replies')
                WHERE p.post_id = %(post_id_from_URL)s
                OR c.post_id = %(post_id_from_URL)s
                OR r.comment_id IN (SELECT comment_id FROM comments WHERE post_id = %(post_id_from_URL)s);
            """
            all_post_media = mysql.query_db(all_related_media_of_post_query, data)

            # Validate the existance of the related media files in the server before deleting them.
            if all_post_media[0]['name']:
                validate_deleted_media_files(all_post_media)

            # Delete the post and it's comments & replies & all related media & likes.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            delete_post_query = """
                DELETE l, m, p
                FROM posts p
                LEFT JOIN comments c ON p.post_id = c.post_id
                LEFT JOIN replies r ON c.comment_id = r.comment_id
                LEFT JOIN media m ON 
                    (p.post_id = m.reference_id AND m.reference_table = 'posts') OR
                    (c.comment_id = m.reference_id AND m.reference_table = 'comments') OR
                    (r.reply_id = m.reference_id AND m.reference_table = 'replies')
                LEFT JOIN likes l ON 
                    (p.post_id = l.reference_id AND l.reference_table = 'posts') OR
                    (c.comment_id = l.reference_id AND l.reference_table = 'comments') OR
                    (r.reply_id = l.reference_id AND l.reference_table = 'replies')
                WHERE p.post_id = %(post_id_from_URL)s
                OR c.post_id = %(post_id_from_URL)s
                OR r.comment_id IN (SELECT comment_id FROM comments WHERE post_id = %(post_id_from_URL)s);
            """
            mysql.query_db(delete_post_query, data)

        return redirect("/dashboard")

    # The signout will redirect to the "/" route.
    return signout()


# Delete a comment with its replies.
@app.route("/dashboard/<comment_id>/delete_comment", methods=["DELETE"])
def delete_comment(comment_id):
    checked_user = check_user_id()
    if checked_user:
        # Check if the logged-in user is the author of the comment.
        data = { 'comment_id_from_URL': comment_id }
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        comment_author_id_query = """
            SELECT user_id FROM comments WHERE comment_id = %(comment_id_from_URL)s;
        """
        comment_author_id = mysql.query_db(comment_author_id_query, data)[0]['user_id']
        if session['user_id'] == comment_author_id:
            # Delete all the media related to the comment, either they are for the comment itself or for its replies.
            # If you want to keep them, although the comment is deleted, just comment out this step and query.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            all_related_media_of_comment_query = """
                SELECT DISTINCT m.name, m.type, m.reference_table
                FROM comments c
                LEFT JOIN replies r ON c.comment_id = r.comment_id
                LEFT JOIN media m ON 
                    (c.comment_id = m.reference_id AND m.reference_table = 'comments') OR
                    (r.reply_id = m.reference_id AND m.reference_table = 'replies')
                WHERE c.comment_id = %(comment_id_from_URL)s
                OR r.comment_id IN (SELECT comment_id FROM replies WHERE comment_id = %(comment_id_from_URL)s);
            """
            all_comment_media = mysql.query_db(all_related_media_of_comment_query, data)

            # Validate the existance of the related media files in the server before deleting them.
            if all_comment_media[0]['name']:
                validate_deleted_media_files(all_comment_media)

            # Delete the comment and its replies & all related media & likes.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            delete_comment_query = """
                DELETE l, m, c
                FROM comments c
                LEFT JOIN replies r ON c.comment_id = r.comment_id
                LEFT JOIN media m ON 
                    (c.comment_id = m.reference_id AND m.reference_table = 'comments') OR
                    (r.reply_id = m.reference_id AND m.reference_table = 'replies')
                LEFT JOIN likes l ON 
                    (c.comment_id = l.reference_id AND l.reference_table = 'comments') OR
                    (r.reply_id = l.reference_id AND l.reference_table = 'replies')
                WHERE c.comment_id = %(comment_id_from_URL)s
                OR r.comment_id IN (SELECT comment_id FROM replies WHERE comment_id = %(comment_id_from_URL)s);
            """
            mysql.query_db(delete_comment_query, data)

        return jsonify(success=True)

    # The signout will redirect to the "/" route.
    return signout()


# Delete a reply.
@app.route("/dashboard/<reply_id>/delete_reply", methods=["DELETE"])
def delete_reply(reply_id):
    checked_user = check_user_id()
    if checked_user:
        # Check if the logged-in user is the author of the reply.
        data = { 'reply_id_from_URL': reply_id }
        mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
        reply_author_id_query = """
            SELECT user_id FROM replies WHERE reply_id = %(reply_id_from_URL)s;
        """
        reply_author_id = mysql.query_db(reply_author_id_query, data)[0]['user_id']
        if session['user_id'] == reply_author_id:
            # Delete all the media related to the reply.
            # If you want to keep them, although the reply is deleted, just comment out this step and query.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            all_related_media_of_reply_query = """
                SELECT DISTINCT m.name, m.type, m.reference_table
                FROM replies r
                LEFT JOIN media m ON 
                    (r.reply_id = m.reference_id AND m.reference_table = 'replies')
                WHERE r.reply_id = %(reply_id_from_URL)s;
            """
            all_reply_media = mysql.query_db(all_related_media_of_reply_query, data)

            # Validate the existance of the related media files in the server before deleting them.
            if all_reply_media[0]['name']:
                validate_deleted_media_files(all_reply_media)

            # Delete the reply & all related media & likes.
            mysql = connectToMySQL('ultimateinventory$ultimate_inventory')
            delete_reply_query = """
                DELETE l, m, r
                FROM replies r
                LEFT JOIN media m ON 
                    (r.reply_id = m.reference_id AND m.reference_table = 'replies')
                LEFT JOIN likes l ON 
                    (r.reply_id = l.reference_id AND l.reference_table = 'replies')
                WHERE r.reply_id = %(reply_id_from_URL)s;
            """
            mysql.query_db(delete_reply_query, data)

        return jsonify(success=True)

    # The signout will redirect to the "/" route.
    return signout()