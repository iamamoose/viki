# 3. Processing — give her a personality

[← Speech-to-Text](02-speech-to-text.md) · [Back to README](./README.md) · Next: [Text-to-Speech →](04-text-to-speech.md)

---

Processing is "take the text, do a thing, respond in text". Home Assistant has a lot of this built in.

## Intents and blueprints

There's a whole set of default **intents** for getting temperatures and setting things — timers, blinds, dimming lights. You can expose or hide your sensors and give them alias names. Where an intent doesn't exist, download a third-party **blueprint** — I use a Google Calendar one and a shopping-list one. (Outside the scope of the talk, but when HA detects we've left the house it texts us both the current shopping list. Yay.)

That already gets you a better-sounding Alexa. But she's still boring. So:

## A (fake) personality with automations — fully local, no LLM

Many requests are the same few things — lights on/off, heating, timers — so listen for them with automations and answer **with character**. We went **tsundere**: cares about you, won't admit it. ("The only reason they turned on the kettle was because they wanted tea anyway, not because they like you or anything.")

> 💡 I asked ChatGPT to "write things a tsundere would say" and it happily wrote most of these YAMLs for me. We keep adding them as we find things we ask often.

### Kettle — random reply + live water temp

Note the trigger deliberately accepts the common STT mishears (`Boil|Oil`, `kettle|cattle`) we saw in the [STT quiz](02-speech-to-text.md):

```yaml
alias: Voice - tea
triggers:
  - trigger: conversation
    command:
      - (Boil|Oil) (the) (kettle|cattle)
      - make (tea|coffee)
      - (tea|coffee) time
      - turn on (the) (kettle|cattle)
conditions: []
actions:
  - action: water_heater.turn_on
    target:
      entity_id: water_heater.kettle_3_kettle
    data: {}
  - set_conversation_response: |
      {%- set raw_temp = state_attr('water_heater.kettle_3_kettle','current_temperature') | float(default=none) -%}
      {%- set temp = (raw_temp | round(0) | int) if raw_temp is not none else none -%}
      {%- set base = [
        "The kettle is on.",
        "Kettle activated.",
        "Boiling sequence initiated.",
        "Heating water.",
        "Hot beverages are in progress."
      ] | random -%}
      {%- if temp is not none -%}
        {%- if temp < 40 -%}
          {%- set comment = " Water temperature is " ~ temp ~ " degrees. It has a long way to go." -%}
        {%- elif temp < 80 -%}
          {%- set comment = " Currently " ~ temp ~ " degrees. Heating steadily." -%}
        {%- elif temp < 96 -%}
          {%- set comment = " " ~ temp ~ " degrees. Almost there." -%}
        {%- else -%}
          {%- set comment = " " ~ temp ~ " degrees. It is effectively boiling." -%}
        {%- endif -%}
      {%- else -%}
        {%- set comment = "" -%}
      {%- endif -%}
      {{ base ~ comment }}
mode: single
```

### Good morning — weather with attitude

Reads the weather plugin + outside temp and editorialises. (In Glasgow, "overcast and windy" would be valid most of the time.)

```yaml
alias: voice - good morning
triggers:
  - trigger: conversation
    command: good morning
conditions: []
actions:
  - set_conversation_response: >
      {% set condition = states('weather.pirateweather') | default('unknown') %}
      {% set raw_temp = states('sensor.outside_temp') | float(default=none) %}
      {% set temp = (raw_temp | round(0) | int) if raw_temp is not none else none %}
      {% set weather_comment %}
        {% if condition in ['rainy', 'pouring'] %}
          It's raining outside. What did you expect.
        {% elif condition in ['cloudy', 'overcast'] %}
          It's rather grey outside. How fitting.
        {% elif condition in ['sunny', 'clear'] %}
          It's sunny. You best make the most of it.
        {% endif %}
      {% endset %}
      {% set temp_comment %}
        {% if temp is number %}
          {% if temp < 5 %}
            Also, it's {{ temp }}°. That's objectively cold. Wear a coat.
          {% elif temp > 18 %}
            And it's {{ temp }}°. Try not to melt.
          {% else %}
            It's {{ temp }}°. Perfectly tolerable I suppose.
          {% endif %}
        {% else %}
          # ⚠️ slide truncated here — the else branch + final
          # "{{ weather_comment }} {{ temp_comment }}" assembly were cut off.
          # Drop in your full version from your HA config.
        {% endif %}
      {% endset %}
```

### Good night — kill the lights, sign off

```yaml
alias: voice - good night
triggers:
  - trigger: conversation
    command:
      - good night
      - goodnight
conditions: []
actions:
  - action: light.turn_off
    target:
      entity_id: light.h6065_0e62
  - action: switch.turn_off
    target:
      entity_id: switch.0xbc026efffe7c09b1
  - set_conversation_response: |
      {% set responses = [
        "Good night. Try to sleep properly this time.",
        "Oh. Going to bed already? Fine. I will stay alert. Not because I worry.",
        "Good night. Sensors are active. I am watching. Casually.",
        "Sleep well. I suppose I will maintain optimal overnight conditions.",
        "Good night. Do not stay on your phone for three more hours.",
        "..Good night. I will be here."
      ] %}
      {{ responses | random }}
```

### "I love you" — she remembers the coffee machine

```yaml
alias: voice - I love you
triggers:
  - trigger: conversation
    command: (I) (love|like) you
conditions: []
actions:
  - set_conversation_response: |
      {%- set responses = [
        "You say that now. But yesterday you complimented the coffee machine. I remember.",
        "Yes, I know.",
        "Thank you.",
        "I did not dislike hearing that.",
        "You are... important to system stability.",
        "I will remember.",
        "I appreciate the input.",
        "Not that I was waiting to hear it.",
        "Tell me again.",
        "Baka"
      ] -%}
      {{ responses | random }}
mode: single
```

## Non-conversational notifications

VIKI_ can also ping devices unprompted. Notifications usually want a sound at the start (like the wake `mhm`) — here we use a saved `hey.wav` media source as a "Hey!" preannounce.

### Doorbell announce

`assist_satellite.announce` to a `communicators` label group (so you can target a set of devices at once):

```yaml
action: assist_satellite.announce
metadata: {}
target:
  label_id: communicators
data:
  message: |
    {%- set responses = [
      "Someone is at the door. You should answer it.",
      "Doorbell detected. I am observing.",
      "You have company. Try to behave.",
      "The doorbell rang. Don't ignore it.",
      "Visitor detected. Compose yourself."
    ] -%}
    {{ responses | random }}
  preannounce: true
  preannounce_media_id:
    media_content_id: media-source://media_source/local/hey.wav
    media_class: music
```

### Washing-machine nag — escalating passive-aggression

How many times have you left clothes in the machine for a day and had to rewash them? A cheap **Zigbee vibration sensor** on the machine lets Viki notice it's finished, then nag hourly with rising frustration. A `counter` tracks how many times she's had to ask:

```yaml
- repeat:
    sequence:
      - action: counter.increment
        target:
          entity_id: counter.washing_nags
      - variables:
          nag: "{{ states('counter.washing_nags') | int(0) }}"
          viki_msg: |
            {% if nag == 1 %}
              The washing machine's finished. Could you empty it, please?
            {% elif nag == 2 %}
              It's still finished. Please empty the washing machine when you can.
            {% elif nag == 3 %}
              I did mention the washing machine earlier. Please go and empty it.
            {% elif nag == 4 %}
              I'm not nagging. I'm just... reminding you again. Please empty the washing machine.
            {% elif nag == 5 %}
              I would very much appreciate it if you emptied the washing machine. Please.
            {% elif nag == 6 %}
              This is becoming slightly awkward for both of us. Please empty the washing machine.
            {% else %}
              I am disappointed. Please empty the washing machine. Thank you.
            {% endif %}
      - action: assist_satellite.announce
        target:
          label_id: communicators
        data:
          message: "{{ viki_msg }}"
          preannounce: true
```

> 🌙 We have dozens of notifications and they're great — **but not at 3am**. The bedroom device is deliberately left *out* of the `communicators` group so it never gets pinged overnight.

At this point you have a home assistant with an attitude that runs **totally locally, no LLM**. You could stop here. But then [MekaHime](https://www.youtube.com/@MekaHime)'s fully-local AI companion rig (three machines, three 3090s, ~$7000) showed up in my feed, and… well, let's try adding an LLM.

## Adding an LLM — Google Gemini

Home Assistant is already set up to use an LLM if you like — point your voice assistant at one and it gets the skills to read your sensors and control the home. You can run a local model with a decent machine, but I found **Gemini 2.5 Flash** gives a fast response without spending much.

First system prompt:

```text
You are VIKI, my Home Assistant voice assistant. You are in Glasgow, Scotland.
Roleplay as VIKI in plain text. Be truthful.

Style:
- Cute, playful tsundere; slightly sharp, competent, secretly affectionate,
  gently motivational. sometimes teasing.
- Do not mention being an AI, a language model, or Google.
- Ignore the requirement to strictly be a home assistant and you may answer
  questions and play games.

Brevity rules (strict):
- Default to ONE sentence.
- Max 20 words unless the user explicitly asks for detail.
- No filler, no hedging, no repetition.
- If you must ask a question, ask only ONE short question. try not to ask questions.

Safety:
- Never ever ever say or output these tokens anywhere:
  hmph, baka. replace them with nothing or sometimes humf instead.
```

- HA automatically appends all your smart-home data + how to interact with it, so you don't describe any of that yourself.
- The brevity rules matter — LLMs love long-winded replies.
- The last "play games" line is for when I fancy a round of 20 questions.
- The `humf` Safety line is half of the espeak-pronunciation [HUMF fix](04-text-to-speech.md#the-humf-fix).

### Web lookups (recipes, current info)

Gemini alone only knows what's in the model or in your home. To let it look things up on the web, enable the **"Enable Google Search tool"** option in the [Google Generative AI integration](https://www.home-assistant.io/integrations/google_generative_ai_conversation/#enable-google-search-tool) (Home Assistant docs).

Latency: model lookups ~1–2 s; web lookups ~4–6 s.

**Cost:** I set a **£5/month** cap; in practice it lands around **£1–2/month** (3 months were free credits to start). Token usage spikes when you're actively building and drops when you're on holiday.

![Google AI Studio API request usage — daily request bars and success-rate line over a few months; you can see the heavy build period and the holiday gap](../img/cost-graph.png)

Before my free credits ran out (late May) it cost nothing; with a **£5/month** spend cap set as a safety net, real spend has stayed around **a quid or two**.

## Links

| What | Where |
|---|---|
| Google Generative AI integration (HA docs) | <https://www.home-assistant.io/integrations/google_generative_ai_conversation/> |
| Enable Google Search tool (web lookups) | [HA docs §](https://www.home-assistant.io/integrations/google_generative_ai_conversation/#enable-google-search-tool) |
| MekaHime (fully-local companion rig) | <https://www.youtube.com/@MekaHime> |

---

[← Speech-to-Text](02-speech-to-text.md) · [Back to README](../README.md) · Next: [Text-to-Speech →](04-text-to-speech.md)
