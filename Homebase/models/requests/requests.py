REQUESTS = {
    "budget": {
        "GET": {
            "bills": "Month.monthly_bills",
            "budget": "Month.week_by_week_description",
            "current_month": "Month.current_month",
            "current_month_spending": "Month.transactions_by_category",
            "data_time": "Month.get_last_update",
            "last_month_bills": "Month.average_monthly_bills",
            "salary": "Person.salary"
        },
        "POST": {}
    },
    "monthly_recap": {
        "GET": {
            "monthly_recap": "Year.transactions_by_category_with_change"
        }
    }
}