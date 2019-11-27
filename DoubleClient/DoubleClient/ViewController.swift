//
//  ViewController.swift
//  SockerDemoSwift
//
//  Created by R on 17/10/19.
//  Copyright © 2019 r0bertLiu. All rights reserved.
//

import UIKit

class ViewController: UIViewController, StreamDelegate, DRDoubleDelegate {
    
    // MARK: IB Outlets - Server Connection
    @IBOutlet weak var ConnectionStatus: UILabel!
    @IBOutlet weak var IpAddress: UITextField!
    @IBOutlet weak var PortNumber: UITextField!
    @IBOutlet weak var MegReceived: UILabel!
    
    // MARK: IB Outlets - Double Status
    @IBOutlet weak var DoubleConnectionStatus: UILabel!
    @IBOutlet weak var DoublePoleHeight: UILabel!
    @IBOutlet weak var DoubleKickStand: UILabel!
    @IBOutlet weak var DoubleBatteryStatus: UILabel!
    
    // MARK: Double Control Vars
    private var drive: Float = 0.0
    private var turn: Float = 0.0
    
    // MARK: Double Trave Vars
    private var LeftEncoder: String = "0.0"
    private var RightEncoder: String = "0.0"
    
    // MARK: Socket Stream Vars
    private var inputStream: InputStream?
    private var outputStream: OutputStream?
    private var connected = false {
        didSet {
            //update UI and clean up streams if needed
            if connected {
                ConnectionStatus.text = "Connected"
            } else {
                ConnectionStatus.text = "Not Connected"
                // force parking
                drive = 0;
                turn = 0;
                DRDouble.shared().deployKickstands()
            }
        }
    }
    
    // MARK: Viewer Function
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        DRDouble.shared().delegate = self
    }
    
    
    @IBAction func GetConnect(_ sender: UIButton) {
        let ip: String = IpAddress.text!
        let port: Int = Int(PortNumber.text!)!
        Stream.getStreamsToHost(withName: ip, port: port, inputStream: &inputStream, outputStream: &outputStream)
               
        if inputStream != nil && outputStream != nil {
            inputStream!.delegate = self
            outputStream!.delegate = self
                       
            inputStream!.schedule(in: RunLoop.current, forMode: RunLoop.Mode.default)
            outputStream!.schedule(in: RunLoop.current, forMode: RunLoop.Mode.default)
                       
            inputStream!.open()
            outputStream!.open()
        }
    }

    
    func stream(_ aStream: Stream, handle eventCode: Stream.Event) {
        switch eventCode {
        case Stream.Event.errorOccurred:
            print("CONNECTION ERROR: Connection to the host failed!")
            connected = false
            inputStream?.close();
            inputStream?.remove(from: RunLoop.current, forMode: RunLoop.Mode.default)
            outputStream?.close();
            outputStream?.remove(from: RunLoop.current, forMode: RunLoop.Mode.default)
        case Stream.Event.openCompleted:
            print("CONNECTION COMPLETED")
            connected = true
        case Stream.Event.hasBytesAvailable:
            if aStream == inputStream {
                print("input stream has bytes available")
                // Loop through availible data one byte at a time, processing the byte
                // as an ASCII character corresponding to a specific command.
                
                var input = ""
                var buffer_in :UInt8 = 0

                while inputStream!.hasBytesAvailable {
                    inputStream!.read(&buffer_in, maxLength: 1)
                    input.append(Character(UnicodeScalar(buffer_in)))
                    //MegReceived.text = input
                    //Operation(command: input)
                }
                MegReceived.text = input
                Operation(command: input)
                
            }
        case Stream.Event.hasSpaceAvailable:
            if aStream == outputStream{
                print("output stream has space availabe")
                
                let str1 = DoublePoleHeight.text
                let str2 = DoubleKickStand.text
                let str3 = DoubleBatteryStatus.text
                let output = str1! + "," + str2! + "," + str3! + "," + LeftEncoder + "," + RightEncoder + "\n"
                let data = output.data(using: String.Encoding.utf8, allowLossyConversion: false)!
                let dataMutablePointer = UnsafeMutablePointer<UInt8>.allocate(capacity: data.count)
                data.copyBytes(to: dataMutablePointer, count: data.count)
                let buffer_out = UnsafePointer<UInt8>(dataMutablePointer)

                outputStream!.write(buffer_out, maxLength: data.count)

            }
            
        case Stream.Event.endEncountered:
            print("endEncountered")
            connected = false
            inputStream?.close();
            inputStream?.remove(from: RunLoop.current, forMode: RunLoop.Mode.default)
            outputStream?.close();
            outputStream?.remove(from: RunLoop.current, forMode: RunLoop.Mode.default)
        default:
            print("CONNECTION ERROR")
            connected = false
        }
    }
    
    // MARK: Operation
    func Operation(command: String) {
        if let op = command.last {
            print(op)
            switch op {
            case "f": //forward
                drive = 1
            case "b": //back
                drive = -1
            case "l": //left
                turn = -1
            case "r": //right
                turn = 1
            case "s": //stop drive
                drive = 0
            case "t": //stop turn
                turn = 0
            case "x": //stop drive and turn
                drive = 0
                turn = 0
            case "u":
                DRDouble.shared().poleUp()
            case "d":
                DRDouble.shared().poleDown()
            case "h":
                DRDouble.shared().poleStop()
            case "p":
                Parking()
            default:
                print("Invalid command: \"\(command)\" ")
            }
        }
    }
    
    func Parking() {
        // stop drive double
        drive = 0;
        turn = 0;
        
        if DRDouble.shared().kickstandState == 1 {
            //if out -> change to in
            DRDouble.shared().retractKickstands()
        }else{
            //if in -> change to out
            DRDouble.shared().deployKickstands()
        }
    }
    
    // MARK: Double Control SDK Methods
    func doubleDidConnect(_ theDouble: DRDouble!) {
        DoubleConnectionStatus.text = "on-line"
    }
    
    func doubleDidDisconnect(_ theDouble: DRDouble!) {
        DoubleConnectionStatus.text = "off-line"
    }
    
    func doubleStatusDidUpdate(_ theDouble: DRDouble!) {
        DoublePoleHeight.text = String(DRDouble.shared().poleHeightPercent)
        DoubleKickStand.text = String(DRDouble.shared().kickstandState)
        DoubleBatteryStatus.text = String(DRDouble.shared().batteryPercent)
        
        // low battery
        if DRDouble.shared().batteryPercent < 0.2 {
            // force parking
            drive = 0;
            turn = 0;
            DRDouble.shared().deployKickstands()
        }
        
        // send double basic status
        /*
        if connected && outputStream!.hasSpaceAvailable {
            let test1 = DoublePoleHeight.text
            let test2 = DoubleKickStand.text
            let test3 = DoubleBatteryStatus.text
            let output = test1! + "," + test2! + "," + test3! +  "\n"
            let data = output.data(using: String.Encoding.utf8, allowLossyConversion: false)!
            let dataMutablePointer = UnsafeMutablePointer<UInt8>.allocate(capacity: data.count)
            data.copyBytes(to: dataMutablePointer, count: data.count)
            let buffer_out = UnsafePointer<UInt8>(dataMutablePointer)

            outputStream!.write(buffer_out, maxLength: data.count)
        }
        */
    }
    
    func doubleDriveShouldUpdate(_ theDouble: DRDouble!) {
        DRDouble.shared().variableDrive(drive, turn: turn)
    }
    
    func doubleTravelDataDidUpdate(_ theDouble: DRDouble!) {
        LeftEncoder = String(DRDouble.shared().rightEncoderDeltaInches)
        RightEncoder = String(DRDouble.shared().rightEncoderDeltaInches)
    }
    
    
}


