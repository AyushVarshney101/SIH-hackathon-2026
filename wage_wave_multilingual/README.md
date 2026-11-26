# Wage Wave

Wage Wave is a Django showcase prototype connecting idle farmland, available farmers, and unused farming machinery.

## Run locally

```powershell
python manage.py migrate
python manage.py load_demo_data
python manage.py runserver
```

Open http://127.0.0.1:8000/.

## Demo accounts

All demo accounts use the password `wage-wave-demo`.

| Role | Username |
| --- | --- |
| Land Owner | `demo_land_alice` |
| Land Owner | `demo_land_ben` |
| Land Owner | `demo_land_carla` |
| Labour | `demo_labour_dan` |
| Labour | `demo_labour_emma` |
| Labour | `demo_labour_farah` |
| Labour | `demo_labour_gideon` |
| Machinery Owner | `demo_machine_tractor` |
| Machinery Owner | `demo_machine_harvester` |
| Machinery Owner | `demo_machine_irrigation` |

`load_demo_data` is safe to run repeatedly. It refreshes only records created by this demo dataset, identified by the `demo_` username and `Demo ` project prefixes.
