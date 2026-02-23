# Inventory Bot

This is a Telegram bot developed for plant nursery owners in Pistoia, Italy.

Its purpose is to reduce the time spent responding to customer price requests by streamlining inventory checks across partner nurseries.

## Problem

When preparing quotes for customers, some requested plants may not be available locally.
These plants are often available at nearby partner nurseries.
Owners must manually call colleagues to check:
- Availability
- Price
This process takes time, interrupts workflow and is inefficient during high season.

## Solution

Before the high season, nursery owners assess the stock of their colleagues.
This bot allows them to:
- Digitally create and manage an inventory of partner nurseries
- Quickly check plant availability
- Store pricing information
- Avoid unnecessary phone calls

All through a simple Telegram chat interface.

## Features

- Set stock location (colleague name)
- Search plants from a standardized list
- Fuzzy name matching
- Insert details via: Text message or Voice message
- Save / modify / cancel entries
- Store data in JSON format
- Export to Excel for internal use

## How It Works
### Start the Bot
```
/start
```

Displays an overview and usage instructions.

### Set Stock Location
```
/c <colleague_name>
```

Sets the colleague (inventory owner) for the current session.

Example:
```
/c Gregorio Stesi
```
### Search for a Plant
```
/n <plant_name>
```

The bot uses fuzzy matching to find similar names.
The user must select from a predefined standardized list.
This ensures consistent naming across all entries.

### Insert Plant Details
After selecting a plant:
- Insert price
- Insert availability
- Insert dimensions
- Add notes (optional)

Input can be:
- Text
- Voice message

All collected data is stored locally on the server in .json format.
- Easily convertible to Excel (.xlsx)
- Used internally for quote preparation
