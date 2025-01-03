# Finnnettstasjon

Dette prosjektet kjører et skript på en Ubuntu-server (192.168.113.64) i en Docker-container. Skriptet er konfigurert for å kjøre som en cronjobb.

## Bygge og kjøre containeren

### Bygging av Docker-image
For å bygge Docker-imaget, naviger til prosjektmappen og kjør følgende kommando:

```bash
root@prod-ubudock-22:/home/toringe/Finnnettstasjon# docker build -t finn_nettstasjon .
```

### Kjøring av containeren
For å kjøre containeren, bruk denne kommandoen:

```bash
/usr/bin/docker run --rm --name finn_nettstasjon_env finn_nettstasjon
```

- **--rm**: Sikrer at containeren slettes etter kjøring.
- **--name**: Setter navnet til containeren som `finn_nettstasjon_env`.

## Konfigurasjon av cronjobb
For å kjøre dette skriptet periodisk, opprett en cronjobb på serveren. Eksempel:

1. Rediger crontab:

    ```bash
    crontab -e
    ```

2. Legg til følgende linje for å kjøre skriptet hver time:

    ```bash
    0 * * * * /usr/bin/docker run --rm --name finn_nettstasjon_env finn_nettstasjon
    ```

Denne konfigurasjonen sikrer at Docker-containeren kjøres og slettes hver gang cronjobben trigges.

## Forutsetninger
- Ubuntu-server med Docker installert.
- Tilgang til serveren med root-privilegier.
- Prosjektmappen inneholder en gyldig `Dockerfile`.

## Feilsøking
Hvis noe går galt:
1. Kontroller Docker-loggene:

    ```bash
    docker logs finn_nettstasjon_env
    ```

2. Sjekk om Docker-imaget ble bygget korrekt:

    ```bash
    docker images | grep finn_nettstasjon
    ```

3. Verifiser cronjobben:

    ```bash
    crontab -l
    ```

4. Kontroller om det er konflikter med eksisterende containere:

    ```bash
    docker ps -a
    ```

