from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Order
import speech_recognition as sr
import re
from word2number import w2n
import json
import os
from datetime import datetime
import pyttsx3


def recognize_order(request):
    if request.method == 'POST':
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something...")
            audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            print(f"Recognized text: {text}")

            # Extract seat number using regex and convert words to numbers
            seat_number_match = re.search(r'\bseat number (\w+)\b', text, re.IGNORECASE)
            if seat_number_match:
                try:
                    seat_number_word = seat_number_match.group(1)
                    print(f"Seat number word: {seat_number_word}")
                    seat_number = w2n.word_to_num(seat_number_word)
                    print(f"Seat number: {seat_number}")
                except ValueError:
                    seat_number = None
            else:
                seat_number = None

            # Extract food items
            menu_items = ["burger", "pizza", "sushi", "salad", "pasta"]
            words = text.lower().split()
            order_items = [item for item in menu_items if item in words]
            print(f"Order items: {order_items}")

            if order_items and seat_number:
                # Save the order to the database
                order = Order(customer_name="Customer", seat_number=seat_number, items=", ".join(order_items))
                order.save()

                # Save the order to a JSON file
                order_data = {
                    "id": order.id,
                    "order": order_items,
                    "seat_number": seat_number,
                    "message": "Order received!",
                    "timestamp": datetime.now().isoformat()
                }
                orders_dir = os.path.join(os.path.dirname(__file__), 'order_files')
                if not os.path.exists(orders_dir):
                    os.makedirs(orders_dir)
                order_file = os.path.join(orders_dir, f"order_{order.id}.json")
                with open(order_file, 'w') as file:
                    json.dump(order_data, file)

                return JsonResponse(order_data)
            elif not seat_number:
                return JsonResponse({"message": "Seat number not recognized."})
            else:
                return JsonResponse({"message": "No food items recognized."})
        except sr.UnknownValueError:
            return JsonResponse({"message": "Could not understand the audio."})
        except sr.RequestError as e:
            return JsonResponse({"message": f"Could not request results; {e}"})
    else:
        return render(request, 'orders/recognize_order.html')

def list_orders(request):
    orders_dir = os.path.join(os.path.dirname(__file__), 'order_files')
    orders = []
    if os.path.exists(orders_dir):
        for filename in os.listdir(orders_dir):
            if filename.endswith('.json'):
                with open(os.path.join(orders_dir, filename), 'r') as file:
                    order_data = json.load(file)
                    # Ensure each order has an ID field
                    if "id" not in order_data:
                        order_id = int(re.search(r'order_(\d+)\.json', filename).group(1))
                        order_data['id'] = order_id
                    orders.append(order_data)
    return render(request, 'orders/list_orders.html', {'orders': orders})

def confirm_order(request, order_id):
    orders_dir = os.path.join(os.path.dirname(__file__), 'order_files')
    order_file = os.path.join(orders_dir, f"order_{order_id}.json")
    if os.path.exists(order_file):
        with open(order_file, 'r') as file:
            order_data = json.load(file)
        # Update the order in the database
        order = Order.objects.get(id=order_id)
        order.confirmed = True
        order.save()
        # Update the JSON file
        order_data['message'] = "Order confirmed!"
        with open(order_file, 'w') as file:
            json.dump(order_data, file)

        # Speak the confirmation message
        engine = pyttsx3.init()
        confirmation_message = f"Order confirmed for seat number {order.seat_number}. Your items are {order.items}."
        engine.say(confirmation_message)
        engine.runAndWait()

        # Check the number of JSON files and delete the oldest ones if more than 6
        json_files = sorted([f for f in os.listdir(orders_dir) if f.endswith('.json')],
                            key=lambda x: os.path.getmtime(os.path.join(orders_dir, x)))
        while len(json_files) > 6 :
            os.remove(os.path.join(orders_dir, json_files.pop(0)))

    return redirect('list_orders')
