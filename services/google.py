import aiohttp
import json
import dotenv
from google.oauth2 import service_account
import google.auth.transport.requests
from typing import Callable
from .additional_classes import WorkerWindows
import asyncio
# Базовый класс для работы с Google Sheets
class BasicGoogleSheetsAsyncClient:
    def __init__(self, creds_path: str, spreadsheet_id: str):
        self.creds_path = creds_path
        self.spreadsheet_id = spreadsheet_id
        self._access_token = None

    def _refresh_token(self):
        creds = service_account.Credentials.from_service_account_file(
            self.creds_path,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        creds.refresh(google.auth.transport.requests.Request())
        self._access_token = creds.token

    async def append_row(self, range_name: str, values: list):
        if not self._access_token:
            self._refresh_token()

        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/{range_name}:append"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }
        params = {
            "valueInputOption": "USER_ENTERED"
        }
        body = {
            "values": [values],
            "majorDimension": "ROWS"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, params=params, json=body) as resp:
                if resp.status != 200:
                    raise Exception(f"Google Sheets API error: {resp.status} {await resp.text()}")
                return await resp.json()

    async def read_range(self, range_name: str):
        if not self._access_token:
            self._refresh_token()

        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/{range_name}"
        headers = {
            "Authorization": f"Bearer {self._access_token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    raise Exception(f"Google Sheets API error: {resp.status} {await resp.text()}")
                return await resp.json()
    
    async def get_all_sheets(self):
        if not self._access_token:
            self._refresh_token()

        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}"
        headers = {
            "Authorization": f"Bearer {self._access_token}"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    raise Exception(f"Google Sheets API error: {resp.status} {await resp.text()}")
                data = await resp.json()
                sheets = data.get("sheets", [])
                return [sheet["properties"]["title"] for sheet in sheets]
    

    async def update_cell(self, cell_range: str, value: str):
        if not self._access_token:
            self._refresh_token()

        url = f"https://sheets.googleapis.com/v4/spreadsheets/{self.spreadsheet_id}/values/{cell_range}"
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }
        params = {
            "valueInputOption": "USER_ENTERED"
        }
        body = {
            "values": [[value]],  # Один элемент — одна строка, содержащая одну ячейку
            "majorDimension": "ROWS"
        }

        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, params=params, json=body) as resp:
                if resp.status != 200:
                    raise Exception(f"Google Sheets API error: {resp.status} {await resp.text()}")
                return await resp.json()




class GoogleSheetsManager(BasicGoogleSheetsAsyncClient):
    def __init__(self, creds_path: str, spreadsheet_id: str):
        super().__init__(creds_path, spreadsheet_id)
    
    async def get_sheet_data(self, sheet_name: str):
        sheet_data = await self.read_range(f"{sheet_name}")
        print(sheet_data)
        return sheet_data


    async def get_worker_names(self):
        sheets = await self.get_all_sheets()
        return sheets
    

    async def get_worker_windows(self, worker_name: str):
        sheet_data = await self.get_sheet_data(worker_name)
        return WorkerWindows(worker_name, sheet_data)
    
    async def reserve_window(self, customer_name: str, worker_name: str, date: str, time: str):
        sheet_data = await self.get_sheet_data(worker_name)
        COLS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        ROWS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26"]
        row = 0
        for i in range(len(sheet_data['values'])):
            if sheet_data['values'][i][0] == date:
                row = i
                break
        col = 0
        for i in range(1, len(sheet_data['values'][0])):
            if sheet_data['values'][0][i] == time:
                col = i
                break
        cell_range = f"{worker_name}!{COLS[col]}{ROWS[row]}"
        await self.update_cell(cell_range, customer_name)
        return True


async def main():
    spreadsheet_id = "18VRf8ZSELiz31dvjYSpNZRF4qwEdqLL5qF9vj1yKxCc"
    creds_path = "google_credentials.json"
    client = GoogleSheetsManager(creds_path, spreadsheet_id)
    sheets = await client.get_worker_names()
    print(sheets)

    name = input("Enter worker name: ")
    windows = await client.get_worker_windows(name)
    print(windows.get_dates())
    date = input("Enter date: ")
    windows = windows.get_windows(date)
    print(windows)
    time = input("Enter time: ")
    await client.reserve_window("Володька", name, date, time)


if __name__ == "__main__":
    asyncio.run(main())
    