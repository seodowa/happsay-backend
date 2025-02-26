# Happsay Backend API Reference

## Get todolist items
* ### Request
    * **Method:** Get
    * **URL:** `/api/todolist/`

* ### Response 
    * **Status Code:** `200 OK`
    * **Content:**
        ```json
        [
            {
                "id": 1,
                "title": "title",
                "content": "content",
                "is_done": false,
                "is_archived": false,
                "deadline": "2022-12-12T00:00:00Z"
            },
        }
        ```

## Login
* ### Request
    * **Method:** POST
    * **URL:** `/api/login/`
    * **Body:**
        ```json
        {
            "username": "username",
            "password": "password"
        }
        ```

* ### Response 
    * **Status Code:** `200 OK`
    * **Content:**
        ```json
        {
            "user": {
                "id": 2,
                "username": "username",
                "email": "email@test.com"
            },
            "refresh": "refresh_token",
            "access": "access_token",
            "redirect_url": "/todolist/"
        }
        ```

## Register
* ### Request
    * **Method:** POST
    * **URL:** `/api/register/`
    * **Body:**
        ```json
        {
            "username": "username",
            "email": "email",
            "password": "password",
            "password2": "confirm_password"
        }
        ```

* ### Response 
    * **Status Code:** `201 CREATED`
    * **Content:**
        ```json       
        {
            "message": "User registered successfully"
        }
        ```

## Updating User Details
* ### Request
    * **Method:** PUT/PATCH
    * **URL:** `/api/users/<id>`
    * **Body:**
        ```json
        {
            "username": "username",
            "email": "email",
            "password": "password",
            "password2": "confirm_password"
        }
        ```

* ### Response 
    * **Status Code:** `200 OK`
    * **Content:**
        ```json       
        {
            "message": "Update successful"
        }
        ```

# TBA