[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/RomiconEZ/AgentBot">
    <img src="readme_images/agentbot_logo.png" alt="Logo" width="150" height=auto>
  </a>

  <h3 align="center">Agent Telegram Bot</h3>
<h3 align="center">(Part of the contact center automation service)</h3>

  <p align="center">
    <br />
    <br />
    <a href="https://github.com/RomiconEZ/AgentBot/issues">Report Bug</a>
    ·
    <a href="https://github.com/RomiconEZ/AgentBot/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents / Содержание</summary>
  <ol>
    <li>
      <a href="#about-the-project--о-проекте">About The Project / О проекте</a>
      <ul>
        <li><a href="#built-with--технологический-стек">Built With / Технологический стек</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started--начало">Getting Started / Начало</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation--установка">Installation / Установка</a></li>
         <li><a href="#additionally">Additionally / Дополнительно</a></li>
         <li><a href="#chatbot-commands">Chatbot Commands / Команды чат-бота</a></li>
      </ul>
    </li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact--контакты">Contact / Контакты</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project / О проекте

Link to project in GitHub: https://github.com/RomiconEZ/AgentBot

#### = ENG =
This Telegram Bot is part of the [contact center automation system for the travel industry](https://github.com/RomiconEZ/Contact-Center-Automation-Service ).

It provides functions for working with clients to travel agents.

The main goals of the bot:
* Sending information about waiting clients to agents so that they can contact them; 
* editing information about agents
* receiving feedback in excel format
* basic functions (add/delete/update/get all in excel format) for tours
(in the future, users will be able to search for tours through text queries according to their wishes)

#### = RU =
Данный Telegram Бот является частью [системы автоматизации контакт-центра для тур-бизнеса](https://github.com/RomiconEZ/Contact-Center-Automation-Service).

Он предоставляет функции для работы с клиентами агентам тур-бизнеса.

Основные цели бота:
* отправление информации об ожидающих клиентах агентам, чтобы они могли с ними связаться; 
* редактирование информации об агентах
* получение отзывов в формате excel
* базовые функции(добавление/удаление/обновление/получение всех в excel формате) для туров
(в дальнейшем пользователям будет доступен поиск туров через текстовые запросы по их желаниям)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With / Технологический стек

* ![Python][Python.com]
* <img src="readme_images/aiogram_logo.png" alt="lc_ch" style="width:100px; height:auto;">
* ![Docker][Docker.com]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started / Начало

### Prerequisites
- Docker: https://www.docker.com/get-started

### Installation / Установка

1. Clone the repository.

2. Copy the `.env.example` file in the directory and change the name to `.env`. Customize the env file for your project.

3. Compile locales with a separate command
   ```shell
   pybabel compile -d bot/locales
   ```
4. Launch the Backend Server (https://github.com/RomiconEZ/GenerativeBackend)
   (At the beginning of the bot's work, a request is made to GenerativeBackend to receive telegram ids of superagents to create admin versions of the chat)

5. In the terminal, navigate to the root directory of the cloned repository. Build the Docker containers with the following command:
   ```shell
   docker compose up -d --build
   ```
   Make migrations
   ```shell
   docker compose exec bot alembic upgrade head
   ```

### Additionally
* http://localhost:3005 - Grafana
* http://localhost:5015 - Admin panel


### Chatbot Commands
* **/get_customer** - get a customer in the queue / получить клиента в очереди 
 
  (Client data contains telegram username, summarization of the user's dialogues 
with the bot for the last 5 messages, and date of addition to the queue)
* **/new_chat** - create a new chat / создать новый чат (clear chat history)
* **/get_reviews** - get customer reviews in excel / получить отзывы клиентов в ехсеl
* **/get_agents** - get agents in excel / получить агентов в excel
* **/delete_agent** - delete an agent / удалить агента
* **/add_agent** - add an agent / добавить агента


* **message** - generating a response to a message from LLM / генерация ответа на сообщение от LLM

<!-- LICENSE -->
## License

This project is licensed under the terms of the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license. See the LICENSE file for details.

[![Creative Commons License](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc-sa/4.0/)



<!-- CONTACT -->
## Contact / Контакты

Roman Neronov:
* email: roman.nieronov@gmail.com / roman.nieronov@mail.ru
* telegram: @Romiconchik

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/RomiconEZ/AgentBot.svg?style=for-the-badge
[contributors-url]: https://github.com/RomiconEZ/AgentBot/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/RomiconEZ/AgentBot.svg?style=for-the-badge
[forks-url]: https://github.com/RomiconEZ/AgentBot/network/members
[stars-shield]: https://img.shields.io/github/stars/RomiconEZ/AgentBot.svg?style=for-the-badge
[stars-url]: https://github.com/RomiconEZ/AgentBot/stargazers
[issues-shield]: https://img.shields.io/github/issues/RomiconEZ/AgentBot.svg?style=for-the-badge
[issues-url]: https://github.com/RomiconEZ/AgentBot/issues
[license-shield]: https://img.shields.io/github/license/RomiconEZ/AgentBot.svg?style=for-the-badge
[license-url]: https://github.com/RomiconEZ/AgentBot/blob/dev/LICENSE.txt


[Python.com]: https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white

[Docker.com]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white

