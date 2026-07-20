# Adding New Models

To add a new AI model, edit `modules/models.py`:

```python
"5": {
    "name": "MyModel",
    "api_key": os.getenv("MY_API_KEY"),
    "endpoint": "https://api.mymodel.com/v1/chat"
}

Then add the API key to .env