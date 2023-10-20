---
tags: 
Bibliography: 
Anki tags: 
Anki deck:
---

Este archivo contiene la definición del protocolo de comunicación que se utiliza en el proyecto para el manejo de partidas

# Protocolo de comunicación

## Cliente obtiene el estado de la partida

1. El cliente obtiene el estado de la partida a partir de realizar una petición al servidor 
2. El servidor responde con un JSON que contiene el estado de la partida. 
3. El cliente debe actualizar su estado de acuerdo a la respuesta del servidor.

### Descripción de la respuesta del servidor

La respuesta del servidor es un JSON que describe:

- Que jugador es el que debe jugar (Solo 1 jugador puede jugar/realizar una acción a la vez)
- Que acción debe realizar el jugador (Robar carta, usar carta, defenderse, intercambiar carta)
- La vitalidad de cada jugador (vivo o muerto) 
- _Cuantas cartas tiene en la mano cada jugador (¿Para el próximo sprint?)_
- Una lista de mensajes/alertas/notificaciones que describen lo que está sucediendo en la partida (Intentos de ataques, intercambios realizados, defensas, etc)
- Si el juego terminó o no y quienes fueron los ganadores.
- Una lista de eventos/notificaciones que describen lo que sucedió en la partida (Robo de cartas, ataques, defensas, intercambios, etc)

El último item de la lista es el más importante, ya que es el que usa el cliente para:
- Mostrar notificaciones/alertas al usuario del estado del juego
- Saber que jugador es el que nos esta atacando/pidiendo un intercambio (y con que carta nos ataca)
- Saber que carta usó el jugador para defenderse de nuestro ataque

### Trabajo del cliente al recibir la respuesta del servidor

El cliente se debe encargar de actualizar su estado de acuerdo a la respuesta del servidor. 

Eso significa habilitarle al jugador correspondiente la posibilidad de realizar la acción que le corresponde (Por ejemplo, el botón de robar carta para el jugador 3). 

Para realizar la acción que corresponde es probable que se necesiten más datos que los que se encuentran en la respuesta del servidor. _Por ejemplo, si el jugador debe defenderse, necesita saber que carta se puede utilizar para defenderse._ Esa información no se encuentra en la respuesta del servidor, por lo que el cliente debe solicitarla al servidor mediante una petición. A continuación algunos ejemplos de peticiones de este estilo que puede realizar el cliente:

- Obtener que cartas de la mano del jugador se pueden descartar y cuales se pueden jugar
- Obtener sobre que objetivos/otros jugadores se puede aplicar el efecto de una carta
- Obtener que cartas de la mano del jugador se pueden utilizar para defenderse de cierto ataque

## Cliente pide realizar una acción

Todas las acciones (robar, descatar, jugar carta, defenderse, seleccionar carta para intercambiar) que realiza el cliente son realizadas mediante una petición al servidor.

La respuesta del servidor solo describirá si la petición fue correcta o no.

El resultado de la acción (por ejemplo, si el ataque se completó o si fue defendido) se describe en la respuesta del servidor a la petición de obtener el estado de la partida, en la sección de mensajes/alertas/notificaciones.

## Servidor realiza una acción

Al recibir una petición del cliente, el servidor debe realizar la acción que se le pide (si fuera posible, caso contrario devolvería un error a la petición). 

Para las acciones que necesitan cierta interacción entre varios jugadores, se tendrá una tabla en la BD con las peticiones (completas o incompletas) que se realizaron y a partir de ahí podremos completar o cancelar la acción, según corresponda.

A continuación una descripción de las acciones/flujos que pueden presentarse.

### Robar carta

Cuando el cliente solicita robar una carta, el servidor debe:

1. Darle una carta al jugador que la solicitó (en la BD)
2. Actualizar el estado de la partida para que la acción siguiente a realizar por el jugador sea "usar carta" (en la BD)
3. _Agregar evento de que el jugador X robó una carta (en la BD) (¿Para el próximo sprint?)_

### Descartar carta

Cuando el cliente solicita descartar una carta, el servidor debe:

1. Quitarle la carta al jugador que la solicitó (en la BD)
2. Actualizar el estado de la partida para que la acción siguiente a realizar por el jugador sea "intercambiar" (en la BD)
3. Agregar evento de que el jugador X descartó una carta (en la BD)

### Jugar carta

Cuando el cliente solicita jugar una carta, el servidor debe:

1. Quitarle la carta al jugador que la solicitó (en la BD)
2. Actualizar que el jugador que puede jugar es el que recibió el ataque (en la BD)
3. La acción siguiente a realizar por el jugador sea "defenderse" (en la BD)
4. Agregar evento de que el jugador X atacó al jugador Y (ataque incompleto) (en la BD)

### Defenderse

Extra: El jugador puede decidir no defenderse (porque no tiene cartas disponibles o porque prefiere no defenderse)

Cuando el cliente solicita defenderse, el servidor debe:

1. Quitarle la carta al jugador que la solicitó (en la BD)
2. Robar una carta del mazo y dársela al jugador que se defiende (en la BD)
3. Aplicar el efecto de la carta que se utilizó para defenderse (en la BD)
4. Actualizar que el jugador que puede jugar es el que realizó el ataque (en la BD)
5. Actualizar que la acción siguiente a realizar por el jugador es "intercambiar" (en la BD)
6. Agregar evento de que el jugador X se defendió del jugador Y (en la BD)

Cuando el cliente no se defiende (manda la petición de defenderse sin carta), el servidor debe:

1. Actualizar que el jugador que puede jugar es el que realizó el ataque (en la BD)
2. Actualizar que la acción siguiente a realizar por el jugador es "intercambiar" (en la BD)
3. Aplicar el efecto de la carta que se utilizó para atacar (en la BD)
4. Agregar evento de que el jugador X completó el ataque al jugador Y (en la BD)

## Intercambiar carta (primera persona, la que esta en su turno)

Cuando el cliente solicita intercambiar una carta, el servidor debe:

1. Agregar evento de que el jugador X quiere intercambiar una carta con el jugador Y (en la BD)

## Intercambiar carta (segunda persona, la que no esta en su turno)

Cuando el cliente solicita intercambiar una carta, el servidor debe:

1. Intercambiar las cartas entre los jugadores (en la BD)
2. Actualizar que la acción siguiente a realizar por el jugador es "robar" (en la BD)
3. Actualizar que el jugador que puede jugar es el siguiente que tiene un turno (en la BD)
4. Agregar evento de que el jugador X intercambió una carta con el jugador Y (en la BD)



