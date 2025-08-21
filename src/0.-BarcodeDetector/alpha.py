import cv2
from pyzbar import pyzbar

capture = cv2.VideoCapture(0)
while capture.isOpened():
    ret, frame = capture.read()
    if not ret:
        break

    # Decode the barcodes in the frame
    barcodes = pyzbar.decode(frame)

    for barcode in barcodes:
        # Draw a rectangle around the detected barcode
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        barcodeValue = barcode.data.decode('utf-8')
        cv2.putText(frame, barcodeValue, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow('Barcode Scanner', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
