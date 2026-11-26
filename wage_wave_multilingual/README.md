# Wage Wave

Wage Wave is a Django showcase prototype connecting idle farmland, available farmers, and unused farming machinery.

## Run locally

```powershell
python manage.py migrate
python manage.py load_demo_data
python manage.py runserver
```

Open http://127.0.0.1:8000/.

## Demo data

The demo accounts, profiles, projects, and ratings are defined in
`main/data/demo_data.json`. Run `python manage.py load_demo_data` to load or
refresh that data into Django's database. This JSON file is a demo-data source,
not a replacement for SQLite or the database used for accounts and app changes.

## Deploy to Vercel

This repository keeps the Django app in the `wage_wave_multilingual` folder. In
Vercel, set **Project Settings → Build and Deployment → Root Directory** to
`wage_wave_multilingual`, then redeploy. The Vercel function and routing
configuration are in that folder.

Add a `DJANGO_SECRET_KEY` environment variable in the Vercel project settings
for Production (and Preview if needed). For a custom domain, set
`DJANGO_ALLOWED_HOSTS` to a comma-separated list that includes that domain.

The project currently uses SQLite. Vercel's function filesystem is temporary,
so database changes are not persistent between deployments or function
instances; use a hosted database before relying on saved user data.

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
